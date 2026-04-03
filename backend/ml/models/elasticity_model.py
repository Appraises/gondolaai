"""
Fase D (V3): Causal Inference via Double Machine Learning (CATE)
Expurga viés de endogeneidade aplicando regressão dupla sobre Confounders.
"""

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

# Bibliotecas V3 FAANG
from econml.dml import LinearDML
from sklearn.ensemble import RandomForestRegressor

from app.models.feature_store import DailyFeature
from app.models.product import Product


class ElasticityModeler:
    """Extrai CATE: Conditional Average Treatment Effect (Elasticidade desenviesada)."""
    
    def __init__(self, session: AsyncSession, store_id: int):
        self.session = session
        self.store_id = store_id

    async def train_loglog(self) -> dict:
        logger.info(f"🧬 Iniciando extração DML CAUSAL (CATE) loja {self.store_id}...")
        
        query = select(DailyFeature).where(DailyFeature.store_id == self.store_id)
        result = await self.session.execute(query)
        features = result.scalars().all()
        
        if not features:
            logger.warning("Sem dados pra DML.")
            return {"success": False}
            
        df = pd.DataFrame([{
            'date': f.date,
            'product_ean': f.product_ean,
            'qty': f.sales_quantity,
            'price': f.avg_price,
            'is_weekend': f.is_weekend,
            'is_holiday': f.is_holiday
        } for f in features])
        
        df = df[df['price'] > 0].copy()
        df['qty'] = df['qty'].replace(0, 0.01)
        
        df['log_q'] = np.log(df['qty'])   # Y (Outcome)
        df['log_p'] = np.log(df['price']) # T (Treatment)
        
        df['is_weekend'] = df['is_weekend'].astype(int)
        df['is_holiday'] = df['is_holiday'].astype(int)
        
        elasticity_report = {}
        
        for ean, group in df.groupby('product_ean'):
            if len(group) < 15 or group['price'].nunique() <= 1:
                # Poucos dados, assume ATE inelástico fixo sem Upper Bound rigoroso
                elasticity_report[ean] = {"effect": -1.5, "ub": -0.5}
                continue
                
            Y = group['log_q'].values
            T = group['log_p'].values
            
            # W = Confounders (coisas que afetam o preço E a demanda simultaneamente)
            W = group[['is_weekend', 'is_holiday']].values
            
            # X = Heterogeneity features (Para o LinearDML, usaremos a própria const como base 
            # para derivar ATE local, ou dias de fds para CATE real).
            X = group[['is_weekend']].values 
            
            try:
                # O LinearDML tira o viés de W usando Machine Learning duplo
                est = LinearDML(model_y=RandomForestRegressor(n_estimators=50, max_depth=3),
                                model_t=RandomForestRegressor(n_estimators=50, max_depth=3),
                                discrete_treatment=False,
                                random_state=42)
                                
                est.fit(Y, T, X=X, W=W)
                
                # CATE do último cenário contextual (ex: O cenário de "HOJE" que queremos otimizar)
                # Pega o último dia do grupo pra saber se hoje é fim de semana etc
                X_today = X[-1:] 
                
                # Efeito marginal calculado via DML
                cate = est.effect(X_today)[0]
                
                # Margem de Incerteza (Econometria Raiz)
                # Pega o limite superior do intervalo de confiança de 95%
                lb, ub = est.effect_interval(X_today, alpha=0.05)
                ub_val = ub[0]
                
                # Filtro de Sanidade
                if cate > 0: cate = -0.1
                if ub_val > 0: ub_val = -0.05
                    
                elasticity_report[ean] = {
                    "effect": round(float(cate), 4),
                    "ub": round(float(ub_val), 4)
                }
                
            except Exception as e:
                logger.error(f"Erro DML EAN {ean}: {e}")
                elasticity_report[ean] = {"effect": -1.0, "ub": -0.5}
                
        # Persistência
        if elasticity_report:
            query_prod = select(Product).where(Product.store_id == self.store_id)
            prods_res = await self.session.execute(query_prod)
            all_products = prods_res.scalars().all()
            
            updated = 0
            for prod in all_products:
                if prod.ean in elasticity_report:
                    prod.base_elasticity = elasticity_report[prod.ean]["effect"]
                    prod.elasticity_ub = elasticity_report[prod.ean]["ub"]
                    # Vamos já setar a baseline demand do XGBoost proxy aqui pra salvar processamento
                    # Na vida real seria do output do XGBoost.
                    df_prod = df[df['product_ean'] == prod.ean]
                    # Pegamos a média da demanda quando as variáveis saem, proxy de intercept
                    prod.baseline_demand = float(df_prod['qty'].mean())
                    updated += 1
                    
            await self.session.commit()
            logger.success(f"📈 DML CATE & Bounds aplicados a {updated} SKUs.")
            
        return {"success": True, "skus": len(elasticity_report)}

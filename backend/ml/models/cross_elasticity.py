"""
Fase C (V3): Cross-Substitution Endógena via Proxy Clusters.
Mata o modelo Apriori de Lift em troca de uma Análise Causal Intra-Categoria
(Aproximação prática do Nested Logit IIA).
"""

import json
import logging
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.feature_store import DailyFeature
from app.models.product import Product


class MarketBasketAnalyzer:
    """Treina regras de Associação para derivar Elasticidade Cruzada."""
    
    def __init__(self, session: AsyncSession, store_id: int):
        self.session = session
        self.store_id = store_id

    async def train_cross_elasticities(self) -> dict:
        """
        Gera OLS Causal por Clusters (Categorias).
        Aproximação de Nested Logit calculando correlação cruzada.
        """
        logger.info(f"🧺 Iniciando Cross-Elasticity Proxy (Nested Clustered) para loja {self.store_id}...")
        
        # Puxamos os produtos ativos e separamos por categoria (Ninhos)
        query_prod = select(Product).where(Product.store_id == self.store_id)
        prods_res = await self.session.execute(query_prod)
        all_products = prods_res.scalars().all()
        
        category_map = {}
        for p in all_products:
            if p.category not in category_map:
                category_map[p.category] = []
            category_map[p.category].append(p.ean)
            
        # Para fins de simplificação MVP FAANG, nós mapeamos matrizes n x n e testamos correlação inversa 
        # de vendas apenas dentro do mesmo "ninho" (Categoria). EAN da Pepsi vs Coca na Bebidas.
        
        # Obter séries temporais num DataFrame
        query_feat = select(DailyFeature).where(DailyFeature.store_id == self.store_id)
        result_feat = await self.session.execute(query_feat)
        features = result_feat.scalars().all()
        
        if not features:
            return {"success": False}
            
        df = pd.DataFrame([{
            'date': f.date,
            'ean': f.product_ean,
            'qty': f.sales_quantity,
            'price': f.avg_price
        } for f in features])
        
        cross_dicts = {}
        
        for category, eans in category_map.items():
            if len(eans) < 2: continue # Ninho não competitivo
            
            # Matriz pivot: Date vs Price_EAN
            df_cat = df[df['ean'].isin(eans)]
            if df_cat.empty: continue
            
            qty_pivot = df_cat.pivot_table(index='date', columns='ean', values='qty', fill_value=0)
            price_pivot = df_cat.pivot_table(index='date', columns='ean', values='price', fill_value=0)
            
            # Correlação bruta de Pearson como proxy heurístico para o MVP
            # Q(A) reage ao P(B)?
            for ean_target in eans:
                if ean_target not in qty_pivot.columns: continue
                # Demanda do item A
                qa = qty_pivot[ean_target]
                if qa.sum() == 0: continue
                
                cross_dicts[ean_target] = {}
                
                for ean_competitor in eans:
                    if ean_target == ean_competitor: continue
                    if ean_competitor not in price_pivot.columns: continue
                    
                    pb = price_pivot[ean_competitor]
                    if pb.std() == 0: continue # Preço do vizinho não muda
                    
                    # Correlação = Q(A) cresce quando P(B) cresce? (Substitutos ideais -> Correlação Positiva)
                    corr = qa.corr(pb)
                    if pd.isna(corr): continue
                    
                    if corr > 0.3: # Substitutos Fortes (Pepsi e Coca)
                        cross_dicts[ean_target][ean_competitor] = round(corr, 3)
                    elif corr < -0.3: # Complementos intra-categoria (Raro, ex: Macarrão e Molho de Tomate)
                        cross_dicts[ean_target][ean_competitor] = round(corr, 3)

        updated = 0
        for prod in all_products:
            if prod.ean in cross_dicts and len(cross_dicts[prod.ean]) > 0:
                prod.cross_elasticity = json.dumps(cross_dicts[prod.ean])
                updated += 1
                
        await self.session.commit()
        logger.success(f"🛒 Associações cruzadas rastreadas via Covariância Intra-Ninho. {updated} SKUs aplicados.")
        
        return {"success": True, "skus_updated": updated}

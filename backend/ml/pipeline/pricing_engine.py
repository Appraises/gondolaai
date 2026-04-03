import json
import numpy as np
from scipy.optimize import minimize
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.product import Product
from app.models.pricing_suggestion import PricingSuggestion

class PricingEngine:
    """FAANG-Level Pricing Engine. Scipy SLSQP com Lerner Warm-Start e Stock Penalty."""

    def __init__(self, session: AsyncSession, store_id: int):
        self.session = session
        self.store_id = store_id

    async def generate_suggestions(self) -> dict:
        logger.info(f"🚀 V3 NLP Causal Solver Loja {self.store_id}...")

        await self.session.execute(
            delete(PricingSuggestion).where(PricingSuggestion.store_id == self.store_id)
        )

        query = select(Product).where(Product.store_id == self.store_id, Product.is_active == True)
        result = await self.session.execute(query)
        all_products = result.scalars().all()
        
        # Filtrainso só o quem tem modelagem CATE 
        optimizable_products = [p for p in all_products if p.base_elasticity is not None and p.cost_price]

        if not optimizable_products:
            logger.warning("Faltam CATE. Abortando solver.")
            return {"success": False}

        suggestions = []
        categories = set(p.category for p in optimizable_products)
        
        for cat in categories:
            prods_cat = [p for p in optimizable_products if p.category == cat]
            
            p0 = np.array([float(p.unit_price) for p in prods_cat])
            c_cost = np.array([float(p.cost_price) for p in prods_cat])
            stock = np.array([float(p.stock_qty) for p in prods_cat])
            
            # CATE \epsilon(x) e Upper Bound \epsilon_{ub}
            elasticities = np.array([float(p.base_elasticity) for p in prods_cat])
            elasticities_ub = np.array([float(p.elasticity_ub) if p.elasticity_ub else float(p.base_elasticity) for p in prods_cat])
            
            # Ponto de Ancora para Reconstrução Contínua (Q(p0))
            q_anchor = np.array([float(p.baseline_demand) if p.baseline_demand else 1.0 for p in prods_cat]) 
            
            # Construindo a Demanda Polinomial Taylor Reconstructed
            # Q(p) = Q(p0) * (p/p0)^E
            def demand_function(p_vec):
                return q_anchor * np.power(p_vec / p0, elasticities)
            
            # Warm Start via Lerner Index (Sanity Check)
            p_warm = np.copy(p0)
            for i in range(len(prods_cat)):
                # Se o Upper Bound da elasticidade for menor que -1.0, o Lerner é seguro
                # Exemplo: UB = -1.5 (Seguro). UB = -0.8 (Inelástico, P_lerner diverge pra infinito!)
                if elasticities_ub[i] < -1.05:
                    p_lerner_local = c_cost[i] / (1.0 + (1.0 / elasticities[i]))
                    # Limita o warm start pra não surtar o optimizer inicial
                    p_warm[i] = np.clip(p_lerner_local, p0[i]*0.7, p0[i]*1.5)
            
            # Objective com Penalidade de Estoque (L2 Smooth)
            def objective(p_vec):
                q_demanded = demand_function(p_vec)
                profit = np.sum((p_vec - c_cost) * q_demanded)
                
                # LAMBDA PENALTY: Se q_demanded ultrapassa o estoque, penalizamos o lucro quadrado e perigosamente
                # Isso resolve o desastre de maximizar lucro hoje esgotando a loja amanhã.
                # Lambda = Lucro Marginal Mediano da categoria
                lambda_penalty = np.median(p0 - c_cost) * 5.0
                stock_out_risk = np.maximum(0, q_demanded - stock)
                penalty = lambda_penalty * np.sum(stock_out_risk**2)
                
                adjusted_profit = profit - penalty
                return -adjusted_profit
                
            # Restrição Física de Domínio Local (Preço +- 25%) evitando extrapolação 
            # de CATE (CATE só é válido na vizinhança de X)
            bounds = []
            for i in range(len(prods_cat)):
                min_p = max(float(c_cost[i]) * 1.01, float(p0[i]) * 0.75) 
                max_p = float(p0[i]) * 1.25
                bounds.append((min_p, max_p))
                
            # Rodar SciPy!
            try:
                res = minimize(objective, p_warm, method='L-BFGS-B', bounds=bounds, options={'maxiter': 100})
                
                if res.success:
                    p_opt = res.x
                    
                    for i, prod in enumerate(prods_cat):
                        delta = (p_opt[i] / p0[i]) - 1.0
                        
                        if abs(delta) > 0.01:
                            # A validação extra: não aceitamos se lucro despencou
                            # Pode acontecer se o L-BFGS-B caiu no vale do estoque e mandou vender mt caro
                            profit_p0 = (p0[i] - c_cost[i]) * q_anchor[i]
                            profit_popt = (p_opt[i] - c_cost[i]) * demand_function(p_opt)[i]
                            
                            if profit_popt >= profit_p0 * 0.95: # Tolera pequena queda de lucro hoje por causa do stock penalty
                                action = "MARKUP" if delta > 0 else "MARKDOWN"
                                
                                sug = PricingSuggestion(
                                    store_id=self.store_id,
                                    product_id=prod.id,
                                    suggested_action=action,
                                    current_price=float(p0[i]),
                                    suggested_price=round(float(p_opt[i]), 2),
                                    margin_impact=round(float(profit_popt - profit_p0), 2),
                                    reason=f"V3 DML: CATE ε={elasticities[i]:.2f} (ub: {elasticities_ub[i]:.2f}). Restrição Lerner/Estoque aplicadas."
                                )
                                suggestions.append(sug)
            except Exception as e:
                logger.error(f"Erro no SLSQP/L-BFGS-B Solver da cat {cat}: {e}")

        self.session.add_all(suggestions)
        await self.session.commit()

        logger.info(f"✅ V3 Pricing Engine gerou {len(suggestions)} algoritmos finais.")
        return {"success": True, "total_suggestions": len(suggestions)}

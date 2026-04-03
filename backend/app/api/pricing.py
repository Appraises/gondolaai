"""
Endpoints de Pricing.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from loguru import logger

from app.database import get_db
from app.models.pricing_suggestion import PricingSuggestion
from app.models.product import Product

router = APIRouter()


@router.get("/suggestions")
async def get_suggestions(
    store_id: int = Query(...),
    action: str = Query(None, description="MARKUP ou MARKDOWN"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Retorna as top recomendações de preço."""
    query = (
        select(PricingSuggestion, Product)
        .join(Product, Product.id == PricingSuggestion.product_id)
        .where(PricingSuggestion.store_id == store_id, PricingSuggestion.is_active == True)
    )

    if action:
        query = query.where(PricingSuggestion.suggested_action == action.upper())

    # Ordenar pelos maiores impactos (seja saving em markdown ou ganho em markup)
    query = query.order_by(desc(PricingSuggestion.margin_impact)).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    suggestions = []
    for sug, prod in rows:
        pct_diff = ((sug.suggested_price / sug.current_price) - 1) * 100
        suggestions.append({
            "id": sug.id,
            "product_id": prod.id,
            "product_name": prod.name,
            "product_ean": prod.ean,
            "category": prod.category,
            "stock_qty": prod.stock_qty,
            "suggested_action": sug.suggested_action,
            "current_price": round(sug.current_price, 2),
            "suggested_price": round(sug.suggested_price, 2),
            "percentage_change": round(pct_diff, 1),
            "margin_impact": round(sug.margin_impact, 2) if sug.margin_impact else 0,
            "reason": sug.reason,
            "generated_at": str(sug.generated_at),
        })

    return suggestions


@router.post("/generate")
async def generate_pricing(
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Dispara a rotina V2 de otimização causal e de preços."""
    from ml.models.elasticity_model import ElasticityModeler
    from ml.pipeline.pricing_engine import PricingEngine
    
    # 1. Atualizar sensibilidade a preço usando a rotina de Statsmodels OLS (Log-Log)
    modeler = ElasticityModeler(session=db, store_id=store_id)
    await modeler.train_loglog()

    # 2. Rodar o Solver do SciPy Constraints e gerar Sugestões
    engine = PricingEngine(session=db, store_id=store_id)
    return await engine.generate_suggestions()

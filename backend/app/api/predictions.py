"""
Endpoints de Predições — Treino de modelos e consulta de previsões.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from loguru import logger

from app.database import get_db
from app.models.prediction import Prediction
from app.models.product import Product

router = APIRouter()


@router.get("/")
async def list_predictions(
    store_id: int = Query(...),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    sort_by: str = Query("pred_7d", description="Ordenar por: pred_7d, pred_14d, pred_30d, confidence"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista predições de demanda para todos os produtos.

    Retorna previsão de vendas para 7, 14 e 30 dias,
    confiança do modelo e dados do produto.
    """
    query = (
        select(Prediction, Product)
        .join(Product, Product.id == Prediction.product_id)
        .where(Prediction.store_id == store_id)
    )

    if category:
        query = query.where(Product.category == category)

    result = await db.execute(query)
    rows = result.all()

    predictions = []
    for pred, product in rows:
        avg_daily = pred.pred_7d / 7 if pred.pred_7d > 0 else 0
        days_of_stock = product.stock_qty / avg_daily if avg_daily > 0 else 999

        predictions.append({
            "product_id": product.id,
            "ean": product.ean,
            "name": product.name,
            "category": product.category,
            "current_stock": product.stock_qty,
            "pred_7d": pred.pred_7d,
            "pred_14d": pred.pred_14d,
            "pred_30d": pred.pred_30d,
            "avg_daily_demand": round(avg_daily, 1),
            "days_of_stock": round(days_of_stock, 1),
            "confidence": pred.confidence,
            "model_version": pred.model_version,
            "generated_at": str(pred.generated_at),
            "status": (
                "🔴 Ruptura iminente" if days_of_stock < 2
                else "🟡 Estoque baixo" if days_of_stock < 5
                else "🟢 OK"
            ),
        })

    # Ordenar
    sort_key = sort_by if sort_by in ["pred_7d", "pred_14d", "pred_30d", "confidence"] else "pred_7d"
    predictions.sort(key=lambda x: x.get(sort_key, 0), reverse=True)

    return predictions[:limit]


@router.post("/train")
async def train_models(
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Treina os modelos de ML (XGBoost + Prophet).
    Em produção, roda semanalmente via Celery.
    """
    from ml.pipeline.training import TrainingPipeline

    logger.info(f"🚀 Treino manual disparado para loja {store_id}")
    pipeline = TrainingPipeline(session=db, store_id=store_id)
    report = await pipeline.run()
    return report


@router.post("/generate")
async def generate_predictions(
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Gera predições para todos os produtos.
    Em produção, roda diariamente via Celery.
    """
    from ml.pipeline.inference import InferencePipeline

    logger.info(f"🔮 Inferência manual disparada para loja {store_id}")
    pipeline = InferencePipeline(session=db, store_id=store_id)
    report = await pipeline.run()
    return report

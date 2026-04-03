"""
Endpoints de Features — Consulta e geração de features para ML.
"""

from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from loguru import logger

from app.database import get_db
from app.models.feature_store import DailyFeature
from app.models.product import Product

router = APIRouter()


@router.get("/")
async def list_features(
    store_id: int = Query(...),
    product_id: Optional[int] = Query(None, description="Filtrar por produto"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    days: int = Query(30, ge=1, le=180, description="Últimos N dias"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista features pré-calculadas.

    Retorna 1 linha por produto por dia com todas as features
    de lag, rolling, calendário, clima e produto.
    """
    from datetime import timedelta
    start_date = date.today() - timedelta(days=days)

    query = (
        select(DailyFeature)
        .where(
            DailyFeature.store_id == store_id,
            DailyFeature.date >= start_date,
        )
    )

    if product_id:
        query = query.where(DailyFeature.product_id == product_id)

    if category:
        query = query.where(DailyFeature.category == category)

    query = query.order_by(desc(DailyFeature.date)).offset(skip).limit(limit)
    result = await db.execute(query)
    features = result.scalars().all()

    return [
        {
            "product_id": f.product_id,
            "date": str(f.date),
            "sales_qty": f.sales_qty,
            "sales_lag_1d": f.sales_lag_1d,
            "sales_lag_7d": f.sales_lag_7d,
            "rolling_mean_7d": f.rolling_mean_7d,
            "rolling_mean_30d": f.rolling_mean_30d,
            "rolling_std_7d": f.rolling_std_7d,
            "day_of_week": f.day_of_week,
            "is_holiday": f.is_holiday,
            "days_until_holiday": f.days_until_holiday,
            "temp_max": f.temp_max,
            "precipitation_mm": f.precipitation_mm,
            "category": f.category,
            "unit_price": f.unit_price,
            "margin": f.margin,
            "stock_qty": f.stock_qty,
            "days_of_stock": f.days_of_stock,
            "days_until_expiry": f.days_until_expiry,
        }
        for f in features
    ]


@router.get("/stats")
async def feature_stats(
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Estatísticas da feature store."""
    result = await db.execute(
        select(
            func.count(DailyFeature.id).label("total_rows"),
            func.count(func.distinct(DailyFeature.product_id)).label("total_products"),
            func.min(DailyFeature.date).label("date_from"),
            func.max(DailyFeature.date).label("date_to"),
        ).where(DailyFeature.store_id == store_id)
    )
    row = result.one()

    return {
        "total_rows": row.total_rows,
        "total_products": row.total_products,
        "date_range": {
            "from": str(row.date_from) if row.date_from else None,
            "to": str(row.date_to) if row.date_to else None,
        },
        "status": "✅ Pronto para treino" if row.total_rows > 1000 else "⚠️ Dados insuficientes",
    }


@router.post("/build")
async def build_features(
    store_id: int = Query(...),
    lookback_days: int = Query(92, ge=30, le=365),
    db: AsyncSession = Depends(get_db),
):
    """
    Executa o FeatureBuilder manualmente.
    Em produção, isso roda via Celery às 02:00 AM.
    """
    from ml.features.builder import FeatureBuilder

    logger.info(f"🔨 Build manual de features para loja {store_id}")

    builder = FeatureBuilder(session=db, store_id=store_id)
    df = await builder.build(lookback_days=lookback_days)

    return {
        "success": True,
        "rows_generated": len(df),
        "products": int(df["product_id"].nunique()) if len(df) > 0 else 0,
        "date_range": {
            "from": str(df["date"].min().date()) if len(df) > 0 else None,
            "to": str(df["date"].max().date()) if len(df) > 0 else None,
        },
        "features": list(df.columns) if len(df) > 0 else [],
        "message": f"✅ {len(df)} features geradas com sucesso!",
    }

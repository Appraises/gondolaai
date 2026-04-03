"""
Endpoints de Alertas — Consulta e gestão de alertas inteligentes.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from loguru import logger

from app.database import get_db
from app.models.alert import Alert
from app.models.product import Product

router = APIRouter()


@router.get("/")
async def list_alerts(
    store_id: int = Query(...),
    alert_type: Optional[str] = Query(
        None, description="Filtrar: ruptura, encalhe, pico_demanda, estoque_baixo"
    ),
    severity: Optional[str] = Query(
        None, description="Filtrar: critical, warning, info"
    ),
    unread_only: bool = Query(False, description="Apenas não lidos"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista alertas inteligentes da loja.

    Alertas são gerados pelo motor de regras que cruza
    predições de ML com estoque atual e datas de validade.
    """
    query = (
        select(Alert, Product)
        .join(Product, Product.id == Alert.product_id)
        .where(Alert.store_id == store_id)
    )

    if alert_type:
        query = query.where(Alert.alert_type == alert_type)
    if severity:
        query = query.where(Alert.severity == severity)
    if unread_only:
        query = query.where(Alert.is_read == False)

    # Ordenar: critical primeiro, depois warning, depois info
    severity_order = {
        "critical": 0,
        "warning": 1,
        "info": 2,
    }
    query = query.order_by(Alert.created_at.desc()).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    alerts = []
    for alert, product in rows:
        alerts.append({
            "id": alert.id,
            "product_id": product.id,
            "product_name": product.name,
            "product_ean": product.ean,
            "category": product.category,
            "current_stock": product.stock_qty,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "suggested_action": alert.suggested_action,
            "is_read": alert.is_read,
            "is_acted": alert.is_acted,
            "created_at": str(alert.created_at),
        })

    # Ordenar por severidade
    alerts.sort(key=lambda x: severity_order.get(x["severity"], 9))

    return alerts


@router.get("/summary")
async def alerts_summary(
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Resumo dos alertas por tipo e severidade."""
    result = await db.execute(
        select(
            Alert.alert_type,
            Alert.severity,
            func.count(Alert.id).label("count"),
        )
        .where(Alert.store_id == store_id)
        .group_by(Alert.alert_type, Alert.severity)
    )
    rows = result.all()

    by_type = {}
    by_severity = {}
    total = 0

    for row in rows:
        by_type[row.alert_type] = by_type.get(row.alert_type, 0) + row.count
        by_severity[row.severity] = by_severity.get(row.severity, 0) + row.count
        total += row.count

    return {
        "total": total,
        "by_type": by_type,
        "by_severity": by_severity,
    }


@router.post("/generate")
async def generate_alerts(
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Gera alertas baseados nas predições atuais.
    Em produção, roda diariamente via Celery.
    """
    from ml.pipeline.alert_generator import AlertGenerator

    generator = AlertGenerator(session=db, store_id=store_id)
    report = await generator.generate()
    return report

@router.post("/dispatch")
async def dispatch_alerts(
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    (Sprint 4) Dispara os alertas críticos não lidos ativamente via WhatsApp para os gerentes configurados.
    """
    from app.services.alert_dispatcher import AlertDispatcher

    dispatcher = AlertDispatcher(session=db, store_id=store_id)
    result = await dispatcher.dispatch_pending_alerts()
    return result

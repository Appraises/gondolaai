"""
Endpoints de Vendas — Consulta de histórico e resumos.
"""

from datetime import datetime, timedelta, date
from typing import Optional, List
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.schemas.sale import SaleResponse, SalesSummary

router = APIRouter()


def _get_period_start(period: str) -> datetime:
    """Calcula a data de início para o período solicitado."""
    now = datetime.utcnow()
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - timedelta(days=now.weekday())
        return start.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        return now - timedelta(days=30)  # Padrão: últimos 30 dias


@router.get("/", response_model=List[SaleResponse])
async def list_sales(
    store_id: int = Query(...),
    period: str = Query("today", description="Período: today, week, month, year"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lista vendas do período com itens incluídos."""
    period_start = _get_period_start(period)

    result = await db.execute(
        select(Sale)
        .where(
            Sale.store_id == store_id,
            Sale.timestamp >= period_start,
        )
        .options(selectinload(Sale.items))
        .order_by(desc(Sale.timestamp))
        .offset(skip)
        .limit(limit)
    )
    sales = result.scalars().unique().all()
    return sales


@router.get("/summary", response_model=SalesSummary)
async def sales_summary(
    store_id: int = Query(...),
    period: str = Query("today", description="Período: today, week, month"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    db: AsyncSession = Depends(get_db),
):
    """
    Resumo de vendas do período.

    Retorna: receita total, quantidade de transações, ticket médio,
    top categorias e top produtos.
    """
    period_start = _get_period_start(period)

    # ── Receita total e contagem de transações ──
    base_query = (
        select(
            func.sum(Sale.total).label("revenue"),
            func.count(Sale.id).label("transactions"),
        )
        .where(
            Sale.store_id == store_id,
            Sale.timestamp >= period_start,
        )
    )
    result = await db.execute(base_query)
    row = result.one()

    total_revenue = Decimal(str(row.revenue or 0))
    total_transactions = row.transactions or 0
    avg_ticket = (
        total_revenue / total_transactions if total_transactions > 0 else Decimal("0")
    )

    # ── Top 5 Categorias por receita ──
    cat_query = (
        select(
            Product.category,
            func.sum(SaleItem.unit_price * SaleItem.quantity).label("revenue"),
        )
        .join(SaleItem, SaleItem.sale_id_fk == Sale.id)
        .join(Product, Product.id == SaleItem.product_id)
        .where(
            Sale.store_id == store_id,
            Sale.timestamp >= period_start,
        )
        .group_by(Product.category)
        .order_by(desc("revenue"))
        .limit(5)
    )
    cat_result = await db.execute(cat_query)
    top_categories = [
        {"category": r.category, "revenue": float(r.revenue or 0)}
        for r in cat_result.all()
    ]

    # ── Top 10 Produtos mais vendidos ──
    prod_query = (
        select(
            Product.name,
            Product.ean,
            func.sum(SaleItem.quantity).label("qty_sold"),
            func.sum(SaleItem.unit_price * SaleItem.quantity).label("revenue"),
        )
        .join(SaleItem, SaleItem.sale_id_fk == Sale.id)
        .join(Product, Product.id == SaleItem.product_id)
        .where(
            Sale.store_id == store_id,
            Sale.timestamp >= period_start,
        )
        .group_by(Product.name, Product.ean)
        .order_by(desc("qty_sold"))
        .limit(10)
    )
    prod_result = await db.execute(prod_query)
    top_products = [
        {
            "name": r.name,
            "ean": r.ean,
            "qty_sold": float(r.qty_sold or 0),
            "revenue": float(r.revenue or 0),
        }
        for r in prod_result.all()
    ]

    return SalesSummary(
        period=period,
        total_revenue=total_revenue,
        total_transactions=total_transactions,
        average_ticket=avg_ticket.quantize(Decimal("0.01")),
        top_categories=top_categories,
        top_products=top_products,
    )

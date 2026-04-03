"""
Endpoints de Produtos — Consulta do catálogo.
"""

from datetime import date, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse, ProductSummary

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    store_id: int = Query(..., description="ID da loja"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    low_stock: bool = Query(False, description="Apenas produtos com estoque < 10"),
    expiring_soon: bool = Query(False, description="Produtos vencendo em < 7 dias"),
    search: Optional[str] = Query(None, description="Busca por nome do produto"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista produtos da loja com filtros opcionais.

    Filtros combináveis:
    - **category**: Ex: "Bebidas", "Laticínios"
    - **low_stock**: Estoque abaixo de 10 unidades
    - **expiring_soon**: Vencimento nos próximos 7 dias
    - **search**: Busca parcial no nome
    """
    query = select(Product).where(
        Product.store_id == store_id,
        Product.is_active == True,
    )

    if category:
        query = query.where(Product.category == category)

    if low_stock:
        query = query.where(Product.stock_qty < 10)

    if expiring_soon:
        threshold = date.today() + timedelta(days=7)
        query = query.where(
            Product.expiry_date.isnot(None),
            Product.expiry_date <= threshold,
            Product.expiry_date >= date.today(),  # Exclui já vencidos
        )

    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    query = query.offset(skip).limit(limit).order_by(Product.name)
    result = await db.execute(query)
    products = result.scalars().all()

    # Converter para response com campos calculados
    response = []
    for p in products:
        product_dict = {
            "id": p.id,
            "store_id": p.store_id,
            "external_id": p.external_id,
            "ean": p.ean,
            "name": p.name,
            "category": p.category,
            "unit_price": p.unit_price,
            "cost_price": p.cost_price,
            "stock_qty": p.stock_qty,
            "expiry_date": p.expiry_date,
            "supplier": p.supplier,
            "is_active": p.is_active,
            "last_synced": p.last_synced,
            "margin": p.margin,
            "days_until_expiry": p.days_until_expiry,
        }
        response.append(ProductResponse(**product_dict))

    return response


@router.get("/categories", response_model=List[str])
async def list_categories(
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Lista todas as categorias de produtos da loja."""
    result = await db.execute(
        select(Product.category)
        .where(Product.store_id == store_id, Product.is_active == True)
        .distinct()
        .order_by(Product.category)
    )
    return [row[0] for row in result.all()]


@router.get("/summary", response_model=List[ProductSummary])
async def products_summary(
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Resumo de produtos agrupado por categoria."""
    # Total por categoria
    result = await db.execute(
        select(
            Product.category,
            func.count(Product.id).label("total"),
            func.sum(Product.unit_price * Product.stock_qty).label("stock_value"),
        )
        .where(Product.store_id == store_id, Product.is_active == True)
        .group_by(Product.category)
        .order_by(Product.category)
    )
    rows = result.all()

    summaries = []
    threshold_date = date.today() + timedelta(days=7)

    for row in rows:
        # Contar estoque baixo nessa categoria
        low_stock_result = await db.execute(
            select(func.count(Product.id)).where(
                Product.store_id == store_id,
                Product.category == row.category,
                Product.stock_qty < 10,
                Product.is_active == True,
            )
        )
        low_stock_count = low_stock_result.scalar() or 0

        # Contar vencendo em breve
        expiring_result = await db.execute(
            select(func.count(Product.id)).where(
                Product.store_id == store_id,
                Product.category == row.category,
                Product.expiry_date.isnot(None),
                Product.expiry_date <= threshold_date,
                Product.expiry_date >= date.today(),
                Product.is_active == True,
            )
        )
        expiring_count = expiring_result.scalar() or 0

        summaries.append(ProductSummary(
            category=row.category,
            total_products=row.total,
            total_stock_value=Decimal(str(row.stock_value or 0)),
            low_stock_count=low_stock_count,
            expiring_soon_count=expiring_count,
        ))

    return summaries


@router.get("/{ean}", response_model=ProductResponse)
async def get_product_by_ean(
    ean: str,
    store_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Busca um produto pelo código de barras (EAN)."""
    result = await db.execute(
        select(Product).where(
            Product.ean == ean,
            Product.store_id == store_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail=f"Produto com EAN '{ean}' não encontrado")

    return ProductResponse(
        id=product.id,
        store_id=product.store_id,
        external_id=product.external_id,
        ean=product.ean,
        name=product.name,
        category=product.category,
        unit_price=product.unit_price,
        cost_price=product.cost_price,
        stock_qty=product.stock_qty,
        expiry_date=product.expiry_date,
        supplier=product.supplier,
        is_active=product.is_active,
        last_synced=product.last_synced,
        margin=product.margin,
        days_until_expiry=product.days_until_expiry,
    )

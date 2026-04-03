from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Schemas de entrada ──

class SaleItemCreate(BaseModel):
    """Um item de venda importado do CSV."""
    product_ean: str = Field(..., description="EAN do produto vendido")
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount: Decimal = Field(0, ge=0)


class SaleCreate(BaseModel):
    """Uma venda (cupom) importada do CSV."""
    sale_id: str = Field(..., description="ID do cupom fiscal")
    timestamp: datetime
    total: Decimal = Field(..., ge=0)
    payment_method: Optional[str] = None
    items: List[SaleItemCreate] = []


# ── Schemas de saída ──

class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal

    model_config = {"from_attributes": True}


class SaleResponse(BaseModel):
    id: int
    store_id: int
    sale_id: str
    timestamp: datetime
    total: Decimal
    payment_method: Optional[str]
    items: List[SaleItemResponse] = []

    model_config = {"from_attributes": True}


class SalesSummary(BaseModel):
    """Resumo de vendas para um período."""
    period: str  # "today", "week", "month"
    total_revenue: Decimal
    total_transactions: int
    average_ticket: Decimal
    top_categories: List[dict]  # [{"category": "Bebidas", "revenue": 1500.00}]
    top_products: List[dict]    # [{"name": "Heineken", "qty_sold": 200}]

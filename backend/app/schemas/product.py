from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# ── Schemas de entrada (criação/importação) ──

class ProductCreate(BaseModel):
    """Schema para criar/importar um produto via CSV ou API."""
    external_id: Optional[str] = None
    ean: str = Field(..., min_length=1, max_length=13, description="Código de barras EAN-13")
    name: str = Field(..., min_length=1, max_length=300)
    category: str = Field(..., min_length=1, max_length=100)
    unit_price: Decimal = Field(..., ge=0, description="Preço de venda")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="Preço de custo")
    stock_qty: int = Field(0, ge=0)
    expiry_date: Optional[date] = None
    supplier: Optional[str] = None


# ── Schemas de saída (resposta da API) ──

class ProductResponse(BaseModel):
    """Schema de resposta ao listar produtos."""
    id: int
    store_id: int
    external_id: Optional[str]
    ean: str
    name: str
    category: str
    unit_price: Decimal
    cost_price: Optional[Decimal]
    stock_qty: int
    expiry_date: Optional[date]
    supplier: Optional[str]
    is_active: bool
    last_synced: datetime
    margin: Optional[float] = None
    days_until_expiry: Optional[int] = None

    model_config = {"from_attributes": True}


class ProductSummary(BaseModel):
    """Resumo de uma categoria de produtos."""
    category: str
    total_products: int
    total_stock_value: Decimal
    low_stock_count: int  # Produtos com estoque < 10
    expiring_soon_count: int  # Produtos vencendo em < 7 dias

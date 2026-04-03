from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Numeric, Integer, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Product(Base):
    """
    Modelo canônico de Produto — formato universal do Gôndola.ai.
    Independente do ERP de origem.

    Conforme definido no implementation_plan.md (Seção 3.1).
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id"), nullable=False, index=True
    )

    # ── Identificação ──
    external_id: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="ID do produto no ERP de origem"
    )
    ean: Mapped[str] = mapped_column(
        String(13), nullable=False, index=True, comment="Código de barras EAN-13"
    )
    name: Mapped[str] = mapped_column(
        String(300), nullable=False, comment="Nome/descrição do produto"
    )
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Categoria: Bebidas, Laticínios, etc."
    )

    # ── Preços ──
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="Preço de venda atual"
    )
    cost_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Custo de compra"
    )

    # ── Estoque ──
    stock_qty: Mapped[int] = mapped_column(
        Integer, default=0, comment="Quantidade em estoque"
    )

    # ── Validade ──
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="Data de validade (quando disponível)"
    )

    # ── Fornecedor ──
    supplier: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="Fornecedor principal"
    )

    # ── Econometria (V2 Pricing Engine) ──
    base_elasticity: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4), nullable=True, comment="Elasticidade de Preço (PED). Ex: -1.5"
    )
    elasticity_ub: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4), nullable=True, comment="Limite Superior do CATE (EconML)"
    )
    cross_elasticity: Mapped[Optional[str]] = mapped_column(
        String(5000), nullable=True, comment="JSON mapping EAN -> Beta Cross-Elasticity"
    )
    baseline_demand: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Demanda base inferida no Scipy NLP"
    )

    # ── Controle ──
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="Última sincronização com ERP"
    )

    # ── Relationships ──
    store: Mapped["Store"] = relationship(back_populates="products")
    sale_items: Mapped[List["SaleItem"]] = relationship(back_populates="product")

    @property
    def margin(self) -> Optional[float]:
        """Calcula margem percentual: (preço - custo) / preço"""
        if self.cost_price and self.unit_price and self.unit_price > 0:
            return float((self.unit_price - self.cost_price) / self.unit_price)
        return None

    @property
    def days_until_expiry(self) -> Optional[int]:
        """Dias até o vencimento. Negativo = já venceu."""
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return None

    def __repr__(self) -> str:
        return f"<Product(ean='{self.ean}', name='{self.name}', stock={self.stock_qty})>"

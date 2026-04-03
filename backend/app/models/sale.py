from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Sale(Base):
    """
    Representa uma venda (cupom fiscal) do supermercado.
    Cada Sale contém múltiplos SaleItems.

    Conforme definido no implementation_plan.md (Seção 3.2).
    """
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id"), nullable=False, index=True
    )

    sale_id: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="ID da transação / cupom no ERP"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, comment="Data e hora da venda"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="Valor total do cupom"
    )
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="Dinheiro, Cartão, PIX"
    )

    # ── Relationships ──
    store: Mapped["Store"] = relationship(back_populates="sales")
    items: Mapped[List["SaleItem"]] = relationship(
        back_populates="sale", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Sale(sale_id='{self.sale_id}', total=R${self.total}, items={len(self.items)})>"


class SaleItem(Base):
    """
    Uma linha do cupom fiscal — um produto vendido.

    Conforme definido no implementation_plan.md (Seção 3.3).
    """
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sale_id_fk: Mapped[int] = mapped_column(
        ForeignKey("sales.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), nullable=False, comment="Quantidade vendida"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="Preço unitário no momento da venda"
    )
    discount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, comment="Desconto aplicado"
    )

    # ── Relationships ──
    sale: Mapped["Sale"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="sale_items")

    @property
    def subtotal(self) -> Decimal:
        """Valor total deste item: (preço * quantidade) - desconto"""
        return (self.unit_price * self.quantity) - self.discount

    def __repr__(self) -> str:
        return f"<SaleItem(product_id={self.product_id}, qty={self.quantity}, price=R${self.unit_price})>"

"""
Pricing Suggestion — Sugestões de ajuste de preço geradas pelo ML.

Sugere markups (aumentos de margem) ou markdowns (reduções de escoamento).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class PricingSuggestion(Base):
    """Sugestão inteligente de preço para um produto."""
    __tablename__ = "pricing_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # ── Sugestão ──
    suggested_action: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="'MARKDOWN' (queima de estoque) ou 'MARKUP' (aumento de margem)"
    )
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    suggested_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # ── Impacto Estimado ──
    margin_impact: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Impacto financeiro estimado (R$) caso acatada"
    )
    reason: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Explicação em linguagem natural (ex: 'Vence em 3 dias')"
    )

    # ── Status ──
    is_active: Mapped[bool] = mapped_column(
        # Quando acatada ou recusada, vira False
        default=True, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<PricingSuggestion(product_id={self.product_id}, "
            f"action='{self.suggested_action}', new_price={self.suggested_price})>"
        )

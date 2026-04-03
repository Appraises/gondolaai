"""
Prediction — Predições de demanda geradas pelo modelo.

Cada linha = 1 produto com predição para 7, 14 e 30 dias.
Regenerada diariamente pelo Inference Pipeline.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Prediction(Base):
    """Predição de demanda gerada pelo ensemble model."""
    __tablename__ = "predictions"

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

    # ── Predições ──
    pred_7d: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Vendas previstas nos próximos 7 dias"
    )
    pred_14d: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Vendas previstas nos próximos 14 dias"
    )
    pred_30d: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Vendas previstas nos próximos 30 dias"
    )

    # ── Metadados ──
    model_version: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Versão do modelo: ensemble_v1_20260401"
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Confiança do modelo (0.0 a 1.0)"
    )

    def __repr__(self) -> str:
        return (
            f"<Prediction(product_id={self.product_id}, "
            f"7d={self.pred_7d}, 14d={self.pred_14d}, 30d={self.pred_30d})>"
        )

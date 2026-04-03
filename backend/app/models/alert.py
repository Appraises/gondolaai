"""
Alert — Alertas inteligentes gerados pelo motor de regras.

Tipos de alerta:
- ruptura:      Estoque vai acabar antes da próxima reposição
- encalhe:      Produto vai vencer com estoque sobrando
- pico_demanda: Demanda prevista muito acima do normal
- estoque_baixo: Estoque baixo mas não crítico ainda
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Alert(Base):
    """Alerta gerado pelo motor de regras + ML."""
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # ── Classificação ──
    alert_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
        comment="ruptura, encalhe, pico_demanda, estoque_baixo"
    )
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="critical, warning, info"
    )

    # ── Mensagem ──
    message: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Mensagem resumida do alerta"
    )
    suggested_action: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Ação sugerida (ex: Fazer pedido de 50 unidades)"
    )

    # ── Status ──
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_acted: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return (
            f"<Alert(type='{self.alert_type}', severity='{self.severity}', "
            f"product_id={self.product_id})>"
        )

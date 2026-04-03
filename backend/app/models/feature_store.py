"""
DailyFeature — Feature Store do Gôndola.ai.

Cada linha representa 1 produto × 1 dia, com TODAS as features
pré-calculadas prontas para alimentar os modelos de ML.

Esta tabela é o "coração" do pipeline de predição:
- Populada pelo FeatureBuilder (job diário às 02:00 AM)
- Consumida pelo Training Pipeline (job semanal)
- Consultada pelo Inference Pipeline (diário às 03:00 AM)
"""

from datetime import date
from typing import Optional

from sqlalchemy import String, Numeric, Integer, Date, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class DailyFeature(Base):
    """Uma linha por produto por dia com todas as features calculadas."""
    __tablename__ = "daily_features"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # ── Target (o que queremos prever) ──
    sales_qty: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Vendas reais desse dia"
    )

    # ── Lag Features ──
    sales_lag_1d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sales_lag_7d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sales_lag_14d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sales_lag_30d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ── Rolling Features ──
    rolling_mean_7d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rolling_mean_30d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rolling_std_7d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ── Estoque ──
    stock_qty: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    days_of_stock: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ── Preço ──
    unit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    margin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ── Calendário ──
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    day_of_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    week_of_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_holiday: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    days_until_holiday: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Clima ──
    temp_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    temp_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precipitation_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rain_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ── Produto ──
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    days_until_expiry: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<DailyFeature(product_id={self.product_id}, date={self.date}, "
            f"sales={self.sales_qty}, mean_7d={self.rolling_mean_7d})>"
        )

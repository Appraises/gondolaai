from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Store(Base):
    """
    Representa um supermercado cadastrado no Gôndola.ai.
    Cada loja é um tenant isolado (multi-tenant por store_id).
    """
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)  # UF: "RJ", "SP"
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # ── WhatsApp / Automação (Sprint 4) ──
    evolution_instance_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Ex: gondolabot_loja1"
    )
    evolution_instance_token: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Senha da instância gerada na Evolution V2"
    )
    manager_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="WhatsApp autorizado a conversar. Ex: 5511999999999"
    )
    alert_phones: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="Destinos dos alertas proativos separados por vírgula"
    )

    # Relationships
    products: Mapped[List["Product"]] = relationship(back_populates="store")
    sales: Mapped[List["Sale"]] = relationship(back_populates="store")

    def __repr__(self) -> str:
        return f"<Store(id={self.id}, name='{self.name}', city='{self.city}/{self.state}')>"

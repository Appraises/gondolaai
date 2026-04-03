"""
Alert Generator — Motor de regras que cruza predições com estoque.

Analisa cada produto e gera alertas quando detecta:
🔴 Ruptura iminente: estoque < 2 dias de vendas previstas
🟡 Estoque baixo: estoque < 5 dias de vendas previstas
📈 Pico de demanda: previsão > 1.5x a média histórica
⏰ Encalhe: produto vai vencer com estoque sobrando
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.product import Product
from app.models.prediction import Prediction
from app.models.alert import Alert


class AlertGenerator:
    """Gera alertas inteligentes baseados em predições + estoque + validade."""

    # Thresholds configuráveis
    RUPTURE_DAYS = 2          # Alerta crítico se estoque dura < N dias
    LOW_STOCK_DAYS = 5        # Warning se estoque dura < N dias
    DEMAND_SPIKE_MULT = 1.5   # Pico se pred > N × média

    def __init__(self, session: AsyncSession, store_id: int):
        self.session = session
        self.store_id = store_id

    async def generate(self) -> dict:
        """
        Gera todos os alertas para a loja.

        Returns:
            Relatório com alertas gerados por tipo e severidade.
        """
        logger.info(f"🚨 Gerando alertas para loja {self.store_id}")

        # Limpar alertas antigos
        await self.session.execute(
            delete(Alert).where(Alert.store_id == self.store_id)
        )

        # Buscar produtos com predições
        products = await self._get_products_with_predictions()
        alerts = []

        for product, prediction in products:
            if not prediction:
                continue

            avg_daily = prediction.pred_7d / 7 if prediction.pred_7d > 0 else 0
            days_of_stock = (
                product.stock_qty / avg_daily if avg_daily > 0 else 999
            )

            # 🔴 RUPTURA IMINENTE
            if days_of_stock < self.RUPTURE_DAYS and avg_daily > 0:
                suggested_qty = int(prediction.pred_7d - product.stock_qty + (avg_daily * 3))
                alert = Alert(
                    store_id=self.store_id,
                    product_id=product.id,
                    alert_type="ruptura",
                    severity="critical",
                    message=(
                        f"⚠️ {product.name} vai ACABAR em {days_of_stock:.0f} dia(s)! "
                        f"Estoque: {product.stock_qty} un | "
                        f"Previsão 7d: {prediction.pred_7d:.0f} un"
                    ),
                    suggested_action=f"Fazer pedido urgente de {max(suggested_qty, 1)} unidades",
                )
                alerts.append(alert)

            # 🟡 ESTOQUE BAIXO
            elif days_of_stock < self.LOW_STOCK_DAYS and avg_daily > 0:
                suggested_qty = int(prediction.pred_14d - product.stock_qty)
                alert = Alert(
                    store_id=self.store_id,
                    product_id=product.id,
                    alert_type="estoque_baixo",
                    severity="warning",
                    message=(
                        f"📦 {product.name} com estoque para {days_of_stock:.0f} dias. "
                        f"Estoque: {product.stock_qty} un | "
                        f"Média diária: {avg_daily:.0f} un"
                    ),
                    suggested_action=f"Programar pedido de {max(suggested_qty, 1)} unidades",
                )
                alerts.append(alert)

            # 📈 PICO DE DEMANDA
            # Comparar pred_7d com a média (usando rolling_mean_30d como referência)
            if avg_daily > 0:
                # Se a previsão 7d é 1.5x acima da média dos últimos 30d × 7
                from app.models.feature_store import DailyFeature
                recent = await self.session.execute(
                    select(DailyFeature.rolling_mean_30d)
                    .where(
                        DailyFeature.product_id == product.id,
                        DailyFeature.store_id == self.store_id,
                    )
                    .order_by(DailyFeature.date.desc())
                    .limit(1)
                )
                row = recent.scalar_one_or_none()
                if row and row > 0:
                    avg_30d_weekly = row * 7
                    if prediction.pred_7d > avg_30d_weekly * self.DEMAND_SPIKE_MULT:
                        alert = Alert(
                            store_id=self.store_id,
                            product_id=product.id,
                            alert_type="pico_demanda",
                            severity="info",
                            message=(
                                f"📈 {product.name}: demanda prevista {prediction.pred_7d:.0f} un "
                                f"(+{((prediction.pred_7d / avg_30d_weekly) - 1) * 100:.0f}% acima da média)"
                            ),
                            suggested_action="Aumentar estoque preventivamente",
                        )
                        alerts.append(alert)

            # ⏰ ENCALHE (validade próxima + estoque alto)
            if product.expiry_date and avg_daily > 0:
                days_until_expiry = (product.expiry_date - date.today()).days
                if days_until_expiry > 0:
                    expected_sales = avg_daily * days_until_expiry
                    excess = product.stock_qty - expected_sales
                    if excess > 0:
                        severity = "critical" if days_until_expiry <= 7 else "warning"
                        discount_pct = min(50, int((excess / product.stock_qty) * 100) + 10)
                        alert = Alert(
                            store_id=self.store_id,
                            product_id=product.id,
                            alert_type="encalhe",
                            severity=severity,
                            message=(
                                f"⏰ {product.name} vence em {days_until_expiry} dias! "
                                f"Estoque: {product.stock_qty} un | "
                                f"Vendas previstas até lá: {expected_sales:.0f} un | "
                                f"Excedente: {excess:.0f} un"
                            ),
                            suggested_action=(
                                f"Aplicar desconto de {discount_pct}% para escoar "
                                f"{int(excess)} unidades antes do vencimento"
                            ),
                        )
                        alerts.append(alert)

        # Salvar alertas
        self.session.add_all(alerts)
        await self.session.commit()

        # Contagem por tipo
        by_type = {}
        by_severity = {}
        for a in alerts:
            by_type[a.alert_type] = by_type.get(a.alert_type, 0) + 1
            by_severity[a.severity] = by_severity.get(a.severity, 0) + 1

        logger.info(
            f"✅ {len(alerts)} alertas gerados | "
            f"Por tipo: {by_type} | Por severidade: {by_severity}"
        )

        return {
            "total_alerts": len(alerts),
            "by_type": by_type,
            "by_severity": by_severity,
        }

    async def _get_products_with_predictions(self) -> list:
        """Busca produtos e suas predições."""
        result = await self.session.execute(
            select(Product)
            .where(Product.store_id == self.store_id, Product.is_active == True)
        )
        products = result.scalars().all()

        items = []
        for product in products:
            pred_result = await self.session.execute(
                select(Prediction).where(
                    Prediction.product_id == product.id,
                    Prediction.store_id == self.store_id,
                )
            )
            prediction = pred_result.scalar_one_or_none()
            items.append((product, prediction))

        return items

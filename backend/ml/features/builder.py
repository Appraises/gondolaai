"""
FeatureBuilder — Orquestrador do pipeline de Feature Engineering.

Este é o "maestro" que coordena todos os módulos de features
e produz o DataFrame final pronto para treinar os modelos de ML.

Fluxo:
1. Extrai vendas diárias do banco (GROUP BY product_id, date)
2. Aplica lag features (vendas passadas)
3. Aplica rolling features (médias móveis)
4. Aplica calendar features (feriados, dia da semana)
5. Busca clima na Open-Meteo API
6. Adiciona product features (categoria, preço, margem)
7. Salva tudo na tabela daily_features
"""

import asyncio
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.feature_store import DailyFeature
from app.config import get_settings

from ml.features.lag_features import add_lag_features
from ml.features.rolling_features import add_rolling_features
from ml.features.calendar_features import add_calendar_features
from ml.features.weather_features import fetch_weather_history, add_weather_features
from ml.features.product_features import add_product_features


class FeatureBuilder:
    """
    Orquestra a construção completa do DataFrame de features.
    Chamado pelo job diário (Celery) ou manualmente.
    """

    def __init__(self, session: AsyncSession, store_id: int):
        self.session = session
        self.store_id = store_id
        self.settings = get_settings()

    async def build(self, lookback_days: int = 92) -> pd.DataFrame:
        """
        Constrói o DataFrame completo de features e salva no banco.

        Args:
            lookback_days: Quantos dias de histórico usar (default 92 = ~3 meses)

        Returns:
            DataFrame com todas as features calculadas.
        """
        logger.info(f"🔨 Iniciando FeatureBuilder para loja {self.store_id} ({lookback_days} dias)")

        # 1. EXTRAIR vendas diárias do banco
        df = await self._extract_daily_sales(lookback_days)
        if df.empty:
            logger.warning("⚠️ Nenhuma venda encontrada para gerar features!")
            return df

        logger.info(f"📊 Dados extraídos: {len(df)} linhas ({df['product_id'].nunique()} produtos)")

        # 2. LAG FEATURES
        df = add_lag_features(df)

        # 3. ROLLING FEATURES
        df = add_rolling_features(df)

        # 4. CALENDAR FEATURES
        df = add_calendar_features(df)

        # 5. WEATHER FEATURES
        weather_df = await fetch_weather_history(
            latitude=self.settings.STORE_LATITUDE,
            longitude=self.settings.STORE_LONGITUDE,
            days_back=lookback_days,
        )
        df = add_weather_features(df, weather_df)

        # 6. PRODUCT FEATURES
        products_df = await self._get_products_dataframe()
        df = add_product_features(df, products_df)

        # 7. SALVAR no banco
        saved = await self._save_features(df)
        logger.info(f"✅ FeatureBuilder completo! {saved} registros salvos em daily_features")

        return df

    async def _extract_daily_sales(self, lookback_days: int) -> pd.DataFrame:
        """
        Extrai vendas diárias agrupadas por produto.
        Resultado: 1 linha por produto por dia.
        """
        start_date = date.today() - timedelta(days=lookback_days)

        # Query: vendas diárias por produto
        query = (
            select(
                SaleItem.product_id,
                func.date(Sale.timestamp).label("date"),
                func.sum(SaleItem.quantity).label("sales_qty"),
            )
            .join(Sale, Sale.id == SaleItem.sale_id_fk)
            .where(
                Sale.store_id == self.store_id,
                Sale.timestamp >= start_date,
            )
            .group_by(SaleItem.product_id, func.date(Sale.timestamp))
            .order_by(SaleItem.product_id, func.date(Sale.timestamp))
        )

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows, columns=["product_id", "date", "sales_qty"])
        df["date"] = pd.to_datetime(df["date"])
        df["sales_qty"] = df["sales_qty"].astype(float)

        # Preencher dias sem venda com 0 (cross join produto × data)
        all_products = df["product_id"].unique()
        all_dates = pd.date_range(start=df["date"].min(), end=df["date"].max(), freq="D")

        full_index = pd.MultiIndex.from_product(
            [all_products, all_dates],
            names=["product_id", "date"]
        )
        df = (
            df.set_index(["product_id", "date"])
            .reindex(full_index, fill_value=0)
            .reset_index()
        )

        return df

    async def _get_products_dataframe(self) -> pd.DataFrame:
        """Busca dados dos produtos como DataFrame para merge."""
        result = await self.session.execute(
            select(
                Product.id,
                Product.category,
                Product.unit_price,
                Product.cost_price,
                Product.stock_qty,
                Product.expiry_date,
            ).where(Product.store_id == self.store_id, Product.is_active == True)
        )
        rows = result.all()
        return pd.DataFrame(
            rows,
            columns=["id", "category", "unit_price", "cost_price", "stock_qty", "expiry_date"]
        )

    async def _save_features(self, df: pd.DataFrame) -> int:
        """Salva features calculadas na tabela daily_features."""
        from sqlalchemy import delete

        # Limpar features anteriores desta loja
        await self.session.execute(
            delete(DailyFeature).where(DailyFeature.store_id == self.store_id)
        )

        # Inserir novos registros
        records = []
        for _, row in df.iterrows():
            feature = DailyFeature(
                store_id=self.store_id,
                product_id=int(row["product_id"]),
                date=row["date"].date() if hasattr(row["date"], "date") else row["date"],
                sales_qty=round(float(row.get("sales_qty", 0)), 2),
                # Lag features
                sales_lag_1d=round(float(row.get("sales_lag_1d", 0)), 2),
                sales_lag_7d=round(float(row.get("sales_lag_7d", 0)), 2),
                sales_lag_14d=round(float(row.get("sales_lag_14d", 0)), 2),
                sales_lag_30d=round(float(row.get("sales_lag_30d", 0)), 2),
                # Rolling features
                rolling_mean_7d=round(float(row.get("rolling_mean_7d", 0)), 2),
                rolling_mean_30d=round(float(row.get("rolling_mean_30d", 0)), 2),
                rolling_std_7d=round(float(row.get("rolling_std_7d", 0)), 2),
                # Calendar features
                day_of_week=int(row.get("day_of_week", 0)),
                day_of_month=int(row.get("day_of_month", 1)),
                week_of_month=int(row.get("week_of_month", 1)),
                is_holiday=bool(row.get("is_holiday", False)),
                days_until_holiday=int(row.get("days_until_holiday", 60)),
                # Weather features
                temp_max=round(float(row.get("temp_max", 25)), 1) if pd.notna(row.get("temp_max")) else None,
                temp_min=round(float(row.get("temp_min", 18)), 1) if pd.notna(row.get("temp_min")) else None,
                precipitation_mm=round(float(row.get("precipitation_mm", 0)), 1) if pd.notna(row.get("precipitation_mm")) else None,
                rain_probability=round(float(row.get("rain_probability", 0)), 2) if pd.notna(row.get("rain_probability")) else None,
                # Product features
                category=str(row.get("category", "")),
                unit_price=round(float(row.get("unit_price", 0)), 2),
                cost_price=round(float(row.get("cost_price", 0)), 2),
                margin=round(float(row.get("margin", 0)), 4),
                stock_qty=int(row.get("stock_qty", 0)),
                days_of_stock=round(float(row.get("days_of_stock", 999)), 1),
                days_until_expiry=int(row["days_until_expiry"]) if pd.notna(row.get("days_until_expiry")) else None,
            )
            records.append(feature)

        # Bulk insert em batches de 500
        batch_size = 500
        for i in range(0, len(records), batch_size):
            self.session.add_all(records[i:i + batch_size])

        await self.session.commit()
        return len(records)

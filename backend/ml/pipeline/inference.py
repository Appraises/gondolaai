"""
Inference Pipeline — Gera predições de demanda para todos os produtos.

Fluxo:
1. Carregar modelos treinados de ml/artifacts/
2. Buscar features mais recentes do banco
3. Para cada produto: prever vendas 7d, 14d, 30d
4. Salvar predições na tabela predictions

Em produção: roda diariamente às 03:00 AM via Celery.
Agora: roda via POST /api/predictions/generate
"""

import os
from datetime import datetime, date

import pandas as pd
import numpy as np
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.feature_store import DailyFeature
from app.models.prediction import Prediction
from ml.models.ensemble import EnsembleModel


ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


class InferencePipeline:
    """Gera predições de demanda para todos os produtos da loja."""

    def __init__(self, session: AsyncSession, store_id: int):
        self.session = session
        self.store_id = store_id

    async def run(self) -> dict:
        """
        Executa a inferência completa.

        Returns:
            Relatório com predições geradas.
        """
        logger.info(f"🔮 Iniciando Inference Pipeline para loja {self.store_id}")

        # 1. Carregar ensemble treinado
        ensemble = EnsembleModel()
        try:
            ensemble.load(ARTIFACTS_DIR)
        except Exception as e:
            return {
                "success": False,
                "error": f"Modelos não encontrados. Rode o treino primeiro. ({e})"
            }

        if not ensemble.is_trained:
            return {"success": False, "error": "Modelos não treinados."}

        # 2. Carregar features recentes (últimos 30 dias)
        features_df = await self._load_recent_features(days=30)
        if features_df.empty:
            return {"success": False, "error": "Nenhuma feature encontrada."}

        # Preparar category_encoded
        categories = sorted(features_df["category"].unique())
        cat_map = {cat: idx for idx, cat in enumerate(categories)}
        features_df["category_encoded"] = features_df["category"].map(cat_map)
        features_df["is_holiday"] = features_df["is_holiday"].astype(int)

        # 3. Gerar predições por produto
        product_ids = features_df["product_id"].unique()
        logger.info(f"📦 Gerando predições para {len(product_ids)} produtos")

        # Limpar predições anteriores
        await self.session.execute(
            delete(Prediction).where(Prediction.store_id == self.store_id)
        )

        predictions_list = []
        model_version = f"ensemble_v1_{datetime.utcnow().strftime('%Y%m%d')}"

        for pid in product_ids:
            product_features = features_df[features_df["product_id"] == pid].copy()
            if product_features.empty:
                continue

            category = product_features["category"].iloc[0]

            # Predições para 7, 14 e 30 dias
            pred_7 = ensemble.predict_product(product_features, category, 7)
            pred_14 = ensemble.predict_product(product_features, category, 14)
            pred_30 = ensemble.predict_product(product_features, category, 30)

            prediction = Prediction(
                store_id=self.store_id,
                product_id=int(pid),
                generated_at=datetime.utcnow(),
                pred_7d=round(pred_7["total_prediction"], 1),
                pred_14d=round(pred_14["total_prediction"], 1),
                pred_30d=round(pred_30["total_prediction"], 1),
                confidence=pred_7["confidence"],
                model_version=model_version,
            )
            self.session.add(prediction)
            predictions_list.append({
                "product_id": int(pid),
                "category": category,
                "pred_7d": pred_7["total_prediction"],
                "pred_14d": pred_14["total_prediction"],
                "pred_30d": pred_30["total_prediction"],
                "confidence": pred_7["confidence"],
            })

        await self.session.commit()

        logger.info(f"✅ {len(predictions_list)} predições geradas")

        return {
            "success": True,
            "store_id": self.store_id,
            "predictions_generated": len(predictions_list),
            "model_version": model_version,
            "sample": predictions_list[:5],  # Primeiros 5 como amostra
        }

    async def _load_recent_features(self, days: int = 30) -> pd.DataFrame:
        """Carrega features dos últimos N dias."""
        from datetime import timedelta
        start_date = date.today() - timedelta(days=days)

        result = await self.session.execute(
            select(DailyFeature)
            .where(
                DailyFeature.store_id == self.store_id,
                DailyFeature.date >= start_date,
            )
            .order_by(DailyFeature.product_id, DailyFeature.date)
        )
        rows = result.scalars().all()

        if not rows:
            return pd.DataFrame()

        data = []
        for r in rows:
            data.append({
                "product_id": r.product_id,
                "date": r.date,
                "sales_qty": r.sales_qty or 0,
                "sales_lag_1d": r.sales_lag_1d or 0,
                "sales_lag_7d": r.sales_lag_7d or 0,
                "sales_lag_14d": r.sales_lag_14d or 0,
                "sales_lag_30d": r.sales_lag_30d or 0,
                "rolling_mean_7d": r.rolling_mean_7d or 0,
                "rolling_mean_30d": r.rolling_mean_30d or 0,
                "rolling_std_7d": r.rolling_std_7d or 0,
                "day_of_week": r.day_of_week or 0,
                "day_of_month": r.day_of_month or 1,
                "week_of_month": r.week_of_month or 1,
                "is_holiday": r.is_holiday or False,
                "days_until_holiday": r.days_until_holiday or 60,
                "temp_max": r.temp_max or 25,
                "precipitation_mm": r.precipitation_mm or 0,
                "rain_probability": r.rain_probability or 0,
                "unit_price": r.unit_price or 0,
                "margin": r.margin or 0,
                "stock_qty": r.stock_qty or 0,
                "category": r.category or "Geral",
            })

        return pd.DataFrame(data)

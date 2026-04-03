"""
Training Pipeline — Treino end-to-end dos modelos.

Fluxo:
1. Ler features do banco (daily_features)
2. Preparar dados (tratar NaN, converter tipos)
3. Treinar EnsembleModel (XGBoost + Prophet)
4. Avaliar no set de validação (MAPE, R²)
5. Salvar modelos em ml/artifacts/
6. Retornar relatório de treino

Em produção: roda semanalmente via Celery.
Agora: roda via POST /api/predictions/train
"""

import os
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.feature_store import DailyFeature
from ml.models.ensemble import EnsembleModel
from ml.pipeline.evaluation import evaluate_predictions, compare_models


ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


class TrainingPipeline:
    """Pipeline end-to-end de treino dos modelos de ML."""

    def __init__(self, session: AsyncSession, store_id: int):
        self.session = session
        self.store_id = store_id

    async def run(self) -> dict:
        """
        Executa o treino completo.

        Returns:
            Relatório com métricas e status do treino.
        """
        logger.info(f"🚀 Iniciando Training Pipeline para loja {self.store_id}")
        start_time = datetime.utcnow()

        # 1. Carregar features
        df = await self._load_features()
        if df.empty or len(df) < 100:
            return {
                "success": False,
                "error": f"Dados insuficientes ({len(df)} linhas). Mínimo: 100.",
            }

        logger.info(f"📊 Features carregadas: {len(df)} linhas, {df['product_id'].nunique()} produtos")

        # 2. Preparar dados
        df = self._prepare_data(df)

        # 3. Split temporal para avaliação
        split_idx = int(len(df) * 0.8)
        df_train = df.iloc[:split_idx]
        df_val = df.iloc[split_idx:]

        logger.info(f"📂 Split: {len(df_train)} treino / {len(df_val)} validação")

        # 4. Treinar ensemble
        ensemble = EnsembleModel()
        ensemble.train(df_train)

        # 5. Avaliar
        y_val = df_val["sales_qty"].values
        y_pred_xgb = ensemble.xgb.predict(df_val)

        metrics = {
            "xgboost": evaluate_predictions(y_val, y_pred_xgb, "XGBoost"),
        }

        # 6. Salvar modelos
        ensemble.save(ARTIFACTS_DIR)

        # 7. Relatório
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        feature_importance = ensemble.feature_importance()
        top_features = dict(list(feature_importance.items())[:10])

        report = {
            "success": True,
            "store_id": self.store_id,
            "training_time_seconds": round(elapsed, 1),
            "data": {
                "total_rows": len(df),
                "train_rows": len(df_train),
                "validation_rows": len(df_val),
                "products": int(df["product_id"].nunique()),
                "date_range": {
                    "from": str(df["date"].min()),
                    "to": str(df["date"].max()),
                },
            },
            "metrics": metrics,
            "best_model": compare_models(metrics) if len(metrics) > 1 else "XGBoost",
            "top_features": top_features,
            "model_version": f"ensemble_v1_{datetime.utcnow().strftime('%Y%m%d')}",
            "artifacts_dir": ARTIFACTS_DIR,
        }

        logger.info(f"✅ Treino completo em {elapsed:.1f}s")
        return report

    async def _load_features(self) -> pd.DataFrame:
        """Carrega features do banco."""
        result = await self.session.execute(
            select(DailyFeature)
            .where(DailyFeature.store_id == self.store_id)
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
                "sales_qty": r.sales_qty,
                "sales_lag_1d": r.sales_lag_1d,
                "sales_lag_7d": r.sales_lag_7d,
                "sales_lag_14d": r.sales_lag_14d,
                "sales_lag_30d": r.sales_lag_30d,
                "rolling_mean_7d": r.rolling_mean_7d,
                "rolling_mean_30d": r.rolling_mean_30d,
                "rolling_std_7d": r.rolling_std_7d,
                "day_of_week": r.day_of_week,
                "day_of_month": r.day_of_month,
                "week_of_month": r.week_of_month,
                "is_holiday": 1 if r.is_holiday else 0,
                "days_until_holiday": r.days_until_holiday,
                "temp_max": r.temp_max,
                "precipitation_mm": r.precipitation_mm,
                "rain_probability": r.rain_probability,
                "unit_price": r.unit_price,
                "cost_price": r.cost_price,
                "margin": r.margin,
                "stock_qty": r.stock_qty,
                "category": r.category,
                "days_until_expiry": r.days_until_expiry,
            })

        return pd.DataFrame(data)

    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa e prepara os dados para treino."""
        # Label encode categoria
        categories = sorted(df["category"].unique())
        cat_map = {cat: idx for idx, cat in enumerate(categories)}
        df["category_encoded"] = df["category"].map(cat_map)

        # Converter booleanos
        if "is_holiday" in df.columns:
            df["is_holiday"] = df["is_holiday"].astype(int)

        # Preencher NaN
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # Ordenar cronologicamente
        df = df.sort_values(["date", "product_id"]).reset_index(drop=True)

        return df

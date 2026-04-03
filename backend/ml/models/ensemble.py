"""
EnsembleModel — Combina Prophet + XGBoost.

Peso: 60% XGBoost + 40% Prophet (conforme architecture doc).

O XGBoost é melhor para capturar relações complexas entre features.
O Prophet é melhor para capturar sazonalidade limpa.
Juntos, cobrem cenários que nenhum dos dois resolveria sozinho.

Se Prophet não estiver disponível, usa 100% XGBoost.
"""

import os
from typing import Optional

import numpy as np
import pandas as pd
from loguru import logger

from ml.models.prophet_model import ProphetWrapper, PROPHET_AVAILABLE
from ml.models.xgboost_model import XGBoostWrapper


class EnsembleModel:
    """Combina Prophet (sazonalidade) + XGBoost (features exógenas)."""

    def __init__(self, xgb_weight: float = 0.6, prophet_weight: float = 0.4):
        self.xgb = XGBoostWrapper()
        self.prophet_models: dict[str, ProphetWrapper] = {}  # 1 por categoria
        self.xgb_weight = xgb_weight
        self.prophet_weight = prophet_weight
        self.is_trained = False

        # Se Prophet não estiver disponível, XGBoost fica 100%
        if not PROPHET_AVAILABLE:
            self.xgb_weight = 1.0
            self.prophet_weight = 0.0
            logger.info("Prophet indisponível → ensemble = 100% XGBoost")

    def train(self, features_df: pd.DataFrame):
        """
        Treina ambos os modelos.

        Args:
            features_df: DataFrame com todas as features do FeatureBuilder.
        """
        logger.info(f"🎯 Treinando Ensemble (XGB:{self.xgb_weight:.0%} + Prophet:{self.prophet_weight:.0%})")

        # 1. Treinar XGBoost (usa TODAS as features)
        self.xgb.train(features_df)

        # 2. Treinar Prophet (1 modelo por categoria)
        if PROPHET_AVAILABLE and self.prophet_weight > 0:
            categories = features_df["category"].unique()
            for cat in categories:
                cat_df = features_df[features_df["category"] == cat].copy()

                # Prophet quer: ds (date) e y (vendas agregadas por dia)
                prophet_df = (
                    cat_df.groupby("date")["sales_qty"]
                    .sum()
                    .reset_index()
                    .rename(columns={"date": "ds", "sales_qty": "y"})
                )

                wrapper = ProphetWrapper()
                wrapper.train(prophet_df, category=cat)
                self.prophet_models[cat] = wrapper

        self.is_trained = True
        logger.info(f"✅ Ensemble treinado | {len(self.prophet_models)} modelos Prophet")

    def predict_product(
        self,
        product_features: pd.DataFrame,
        category: str,
        horizon_days: int = 7,
    ) -> dict:
        """
        Gera predição para um produto específico.

        Args:
            product_features: Features recentes do produto (últimos 7+ dias)
            category: Categoria do produto
            horizon_days: Dias para prever (7, 14, 30)

        Returns:
            {
                "daily_predictions": [...],   # pred diária
                "total_prediction": float,    # soma do período
                "xgb_total": float,           # contribuição XGB
                "prophet_total": float,       # contribuição Prophet
                "confidence": float,          # 0-1
            }
        """
        # XGBoost: gera predição para cada dia futuro simulado
        # Usamos as features mais recentes como base
        xgb_pred = self._predict_xgb_forward(product_features, horizon_days)

        # Prophet: gera predição de série temporal
        prophet_pred = np.zeros(horizon_days)
        if category in self.prophet_models and self.prophet_weight > 0:
            prophet_pred = self.prophet_models[category].predict(horizon_days)
            # Prophet prediz a categoria inteira, precisamos proporção do produto
            n_products_in_cat = max(len(product_features["product_id"].unique()), 1)
            prophet_pred = prophet_pred / n_products_in_cat

        # Combinar
        combined = (self.xgb_weight * xgb_pred) + (self.prophet_weight * prophet_pred)
        combined = np.maximum(combined, 0)  # Nunca negativo

        # Calcular confiança baseada na volatilidade
        if len(product_features) > 1:
            std = product_features["sales_qty"].std()
            mean = product_features["sales_qty"].mean()
            cv = std / mean if mean > 0 else 1.0  # Coeficiente de variação
            confidence = max(0.0, min(1.0, 1.0 - cv))
        else:
            confidence = 0.5

        return {
            "daily_predictions": combined.round(1).tolist(),
            "total_prediction": float(combined.sum().round(0)),
            "xgb_total": float(xgb_pred.sum().round(0)),
            "prophet_total": float(prophet_pred.sum().round(0)),
            "confidence": round(confidence, 2),
        }

    def _predict_xgb_forward(
        self, product_features: pd.DataFrame, horizon_days: int
    ) -> np.ndarray:
        """
        Gera predições XGBoost para N dias futuros.
        Usa a última linha de features como template e simula para frente.
        """
        if not self.xgb.is_trained:
            return np.zeros(horizon_days)

        # Usar a última linha de features como base
        last_row = product_features.iloc[-1:].copy()
        predictions = []

        for day in range(horizon_days):
            pred = self.xgb.predict(last_row)
            predictions.append(float(pred[0]))

            # Atualizar features para o próximo dia (deslocar lags)
            last_row = last_row.copy()
            last_row["sales_lag_1d"] = pred[0]
            last_row["day_of_week"] = (last_row["day_of_week"].values[0] + 1) % 7
            last_row["day_of_month"] = min(last_row["day_of_month"].values[0] + 1, 28)

        return np.array(predictions)

    def feature_importance(self) -> dict:
        """Retorna feature importance do XGBoost."""
        return self.xgb.feature_importance()

    def save(self, artifacts_dir: str):
        """Salva todos os modelos treinados."""
        os.makedirs(artifacts_dir, exist_ok=True)

        self.xgb.save(os.path.join(artifacts_dir, "xgb_model.pkl"))

        for cat, prophet in self.prophet_models.items():
            safe_name = cat.replace(" ", "_").lower()
            prophet.save(os.path.join(artifacts_dir, f"prophet_{safe_name}.json"))

        logger.info(f"💾 Ensemble salvo em {artifacts_dir}")

    def load(self, artifacts_dir: str):
        """Carrega modelos salvos."""
        xgb_path = os.path.join(artifacts_dir, "xgb_model.pkl")
        if os.path.exists(xgb_path):
            self.xgb.load(xgb_path)

        # Carregar Prophets
        if PROPHET_AVAILABLE:
            for f in os.listdir(artifacts_dir):
                if f.startswith("prophet_") and f.endswith(".json"):
                    cat_name = f.replace("prophet_", "").replace(".json", "")
                    wrapper = ProphetWrapper()
                    wrapper.load(os.path.join(artifacts_dir, f))
                    self.prophet_models[cat_name] = wrapper

        self.is_trained = True
        logger.info(f"📂 Ensemble carregado de {artifacts_dir}")

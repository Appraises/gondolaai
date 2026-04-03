"""
ProphetWrapper — Modelo de séries temporais do Facebook.

Captura padrões temporais que o XGBoost não pega bem:
- Sazonalidade semanal (sábado vende mais)
- Sazonalidade anual (dezembro vende mais)
- Tendência de longo prazo (vendas subindo/caindo)
- Efeito de feriados brasileiros

Treinamos 1 modelo Prophet por CATEGORIA (não por SKU),
porque cada categoria tem mais dados = modelo mais robusto.
"""

import json
import os
from typing import Optional

import numpy as np
import pandas as pd
from loguru import logger

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("⚠️ Prophet não instalado. Usando fallback (sem sazonalidade).")


class ProphetWrapper:
    """Wrapper do Facebook Prophet para o Gôndola.ai."""

    def __init__(self):
        self.model: Optional[Prophet] = None
        self.is_trained = False
        self.category: str = ""

    def train(self, df: pd.DataFrame, category: str = "all"):
        """
        Treina um modelo Prophet.

        Args:
            df: DataFrame com colunas ['ds' (date), 'y' (vendas)]
            category: Nome da categoria para logging
        """
        if not PROPHET_AVAILABLE:
            logger.warning("Prophet indisponível, skip do treino.")
            return

        self.category = category
        logger.info(f"🔮 Treinando Prophet para '{category}' ({len(df)} dias)")

        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
            changepoint_prior_scale=0.05,  # Conservador nas mudanças de tendência
        )

        # Adicionar feriados brasileiros
        self.model.add_country_holidays(country_name="BR")

        # Prophet precisa de 'ds' e 'y'
        prophet_df = df[["ds", "y"]].copy()
        prophet_df = prophet_df.dropna()

        # Suprimir logs verbosos do Prophet/cmdstan
        import logging
        logging.getLogger("prophet").setLevel(logging.WARNING)
        logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

        self.model.fit(prophet_df)
        self.is_trained = True
        logger.info(f"✅ Prophet treinado para '{category}'")

    def predict(self, horizon_days: int = 30) -> np.ndarray:
        """
        Gera predições para os próximos N dias.

        Returns:
            Array com predições diárias [day1, day2, ..., dayN]
        """
        if not self.is_trained or not self.model:
            logger.warning("Prophet não treinado, retornando zeros.")
            return np.zeros(horizon_days)

        future = self.model.make_future_dataframe(periods=horizon_days)
        forecast = self.model.predict(future)

        # Pegar apenas os dias futuros (últimos N do forecast)
        predictions = forecast.tail(horizon_days)["yhat"].values

        # Nunca prever vendas negativas
        return np.maximum(predictions, 0)

    def predict_with_intervals(self, horizon_days: int = 30) -> pd.DataFrame:
        """Predição com intervalos de confiança."""
        if not self.is_trained or not self.model:
            return pd.DataFrame()

        future = self.model.make_future_dataframe(periods=horizon_days)
        forecast = self.model.predict(future)

        result = forecast.tail(horizon_days)[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        result.columns = ["date", "prediction", "lower_bound", "upper_bound"]
        return result

    def save(self, path: str):
        """Salva o modelo treinado em JSON (formato serializado do Prophet)."""
        if not self.is_trained or not self.model:
            return

        from prophet.serialize import model_to_json
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(model_to_json(self.model))
        logger.debug(f"Prophet salvo em {path}")

    def load(self, path: str):
        """Carrega modelo salvo."""
        if not PROPHET_AVAILABLE:
            return

        from prophet.serialize import model_from_json
        with open(path, "r") as f:
            self.model = model_from_json(f.read())
        self.is_trained = True
        logger.debug(f"Prophet carregado de {path}")

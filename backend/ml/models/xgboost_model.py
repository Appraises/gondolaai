"""
XGBoostWrapper — Modelo de gradient boosting para features tabulares.

O XGBoost é o cavalo de batalha do ensemble:
- Captura relações não-lineares entre features
- "Se faz calor E é sexta E é perto do pagamento → cerveja 3x"
- Muito rápido para treinar e inferir
- Fornece feature importance (quais variáveis importam mais)
"""

import os
from typing import Optional

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from loguru import logger


class XGBoostWrapper:
    """Wrapper do XGBoost para o Gôndola.ai."""

    # Features que o modelo usa (ordem importa)
    FEATURE_COLUMNS = [
        # Lag features
        "sales_lag_1d", "sales_lag_7d", "sales_lag_14d", "sales_lag_30d",
        # Rolling features
        "rolling_mean_7d", "rolling_mean_30d", "rolling_std_7d",
        # Calendar features
        "day_of_week", "day_of_month", "week_of_month",
        "is_holiday", "days_until_holiday",
        # Weather features
        "temp_max", "precipitation_mm", "rain_probability",
        # Product features
        "unit_price", "margin", "stock_qty", "category_encoded",
    ]

    TARGET = "sales_qty"

    def __init__(self):
        self.model: Optional[xgb.XGBRegressor] = None
        self.is_trained = False
        self.feature_importances_: dict = {}

    def train(self, df: pd.DataFrame, eval_ratio: float = 0.2):
        """
        Treina o XGBoost com split temporal.

        Split temporal: últimos 20% dos dados para validação.
        Isso simula o caso real (prever futuro baseado no passado).

        Args:
            df: DataFrame com FEATURE_COLUMNS + TARGET
            eval_ratio: Proporção dos dados para validação (0.2 = 20%)
        """
        logger.info(f"🌲 Treinando XGBoost ({len(df)} linhas, {len(self.FEATURE_COLUMNS)} features)")

        # Preparar features e target
        available_features = [c for c in self.FEATURE_COLUMNS if c in df.columns]
        X = df[available_features].copy()
        y = df[self.TARGET].copy()

        # Converter booleanos para int
        for col in X.columns:
            if X[col].dtype == bool:
                X[col] = X[col].astype(int)

        # Preencher NaN
        X = X.fillna(0)
        y = y.fillna(0)

        # Split temporal (não aleatório — últimos N% para validação)
        split_idx = int(len(df) * (1 - eval_ratio))
        X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

        logger.info(f"  Split: {len(X_train)} treino / {len(X_val)} validação")

        # Configuração do XGBoost
        self.model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            reg_alpha=0.1,       # L1 regularization
            reg_lambda=1.0,      # L2 regularization
            random_state=42,
            objective="reg:squarederror",
            early_stopping_rounds=20,
            verbosity=0,
        )

        # Treinar com early stopping
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )

        self.is_trained = True
        self._used_features = available_features

        # Guardar feature importance
        importances = self.model.feature_importances_
        self.feature_importances_ = dict(
            sorted(
                zip(available_features, importances),
                key=lambda x: x[1],
                reverse=True,
            )
        )

        logger.info(
            f"✅ XGBoost treinado | "
            f"Best iteration: {self.model.best_iteration} | "
            f"Top 3 features: {list(self.feature_importances_.keys())[:3]}"
        )

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Gera predições para as linhas do DataFrame.

        Args:
            df: DataFrame com as mesmas FEATURE_COLUMNS do treino.

        Returns:
            Array com predições (uma por linha).
        """
        if not self.is_trained or not self.model:
            logger.warning("XGBoost não treinado, retornando zeros.")
            return np.zeros(len(df))

        features = [c for c in self._used_features if c in df.columns]
        X = df[features].copy()

        for col in X.columns:
            if X[col].dtype == bool:
                X[col] = X[col].astype(int)
        X = X.fillna(0)

        predictions = self.model.predict(X)

        # Nunca prever vendas negativas
        return np.maximum(predictions, 0)

    def feature_importance(self) -> dict:
        """Retorna importância de cada feature (para insight/debug)."""
        return self.feature_importances_

    def save(self, path: str):
        """Salva o modelo treinado em disco (.pkl)."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "features": self._used_features,
                "importances": self.feature_importances_,
            },
            path,
        )
        logger.debug(f"XGBoost salvo em {path}")

    def load(self, path: str):
        """Carrega modelo salvo."""
        data = joblib.load(path)
        self.model = data["model"]
        self._used_features = data["features"]
        self.feature_importances_ = data["importances"]
        self.is_trained = True
        logger.debug(f"XGBoost carregado de {path}")

"""
Evaluation — Métricas de qualidade dos modelos.

Métricas calculadas:
- MAPE (Mean Absolute Percentage Error) — meta: < 15%
  "Em média, erramos X% no valor previsto"
- RMSE (Root Mean Squared Error)
  "Erro médio em unidades absolutas"
- MAE (Mean Absolute Error)
  "Erro médio sem considerar outliers"
- R² (Coeficiente de determinação)
  "Quanto da variação o modelo explica (1.0 = perfeito)"
"""

import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error,
)
from loguru import logger


def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model",
) -> dict:
    """
    Calcula todas as métricas de qualidade.

    Args:
        y_true: Vendas reais
        y_pred: Vendas previstas
        model_name: Nome para logging

    Returns:
        Dict com MAPE, RMSE, MAE, R²
    """
    # Remover zeros do y_true para evitar divisão por zero no MAPE
    mask = y_true > 0
    y_true_safe = y_true[mask]
    y_pred_safe = y_pred[mask]

    if len(y_true_safe) == 0:
        logger.warning(f"⚠️ {model_name}: Nenhuma venda real > 0 para avaliar")
        return {"mape": 999, "rmse": 999, "mae": 999, "r2": 0}

    mape = mean_absolute_percentage_error(y_true_safe, y_pred_safe) * 100
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    metrics = {
        "mape": round(mape, 2),
        "rmse": round(rmse, 2),
        "mae": round(mae, 2),
        "r2": round(r2, 4),
    }

    # Emoji baseado na qualidade
    if mape < 10:
        quality = "🏆 Excelente"
    elif mape < 15:
        quality = "✅ Bom"
    elif mape < 25:
        quality = "⚠️ Aceitável"
    else:
        quality = "❌ Precisa melhorar"

    logger.info(
        f"📊 {model_name} | MAPE: {mape:.1f}% ({quality}) | "
        f"RMSE: {rmse:.1f} | MAE: {mae:.1f} | R²: {r2:.3f}"
    )

    return metrics


def compare_models(results: dict[str, dict]) -> str:
    """
    Compara vários modelos e retorna o nome do melhor.

    Args:
        results: {"XGBoost": {...metrics}, "Prophet": {...metrics}}

    Returns:
        Nome do melhor modelo (menor MAPE)
    """
    best_name = min(results, key=lambda k: results[k]["mape"])
    logger.info(
        f"🏆 Melhor modelo: {best_name} "
        f"(MAPE: {results[best_name]['mape']:.1f}%)"
    )
    return best_name

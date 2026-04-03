"""
Weather Features — Dados climáticos da Open-Meteo API.

Captura: "Vai fazer calor no domingo? Vai chover?"
Clima afeta diretamente vendas: calor = +cerveja, +sorvete, +água.
Chuva = menos clientes na loja.

API: https://api.open-meteo.com (gratuita, sem API key)
"""

from datetime import date, timedelta

import httpx
import pandas as pd
from loguru import logger

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


async def fetch_weather_history(
    latitude: float,
    longitude: float,
    days_back: int = 92,
    forecast_days: int = 16,
) -> pd.DataFrame:
    """
    Busca dados climáticos históricos e previsão da Open-Meteo API.

    Args:
        latitude: Latitude da loja (ex: -22.9068 para Rio)
        longitude: Longitude da loja (ex: -43.1729 para Rio)
        days_back: Quantos dias de histórico buscar
        forecast_days: Quantos dias de previsão (max 16 na API gratuita)

    Returns:
        DataFrame com colunas: date, temp_max, temp_min, precipitation_mm, rain_probability
    """
    logger.info(
        f"🌤️ Buscando clima: lat={latitude}, lon={longitude}, "
        f"histórico={days_back}d, previsão={forecast_days}d"
    )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
        ]),
        "past_days": days_back,
        "forecast_days": forecast_days,
        "timezone": "America/Sao_Paulo",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(OPEN_METEO_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        daily = data.get("daily", {})

        df = pd.DataFrame({
            "date": pd.to_datetime(daily["time"]),
            "temp_max": daily.get("temperature_2m_max"),
            "temp_min": daily.get("temperature_2m_min"),
            "precipitation_mm": daily.get("precipitation_sum"),
            "rain_probability": [
                (p / 100.0) if p is not None else 0.0
                for p in daily.get("precipitation_probability_max", [])
            ],
        })

        # Preencher NaN da probabilidade de chuva (histórico nem sempre tem)
        df["rain_probability"] = df["rain_probability"].fillna(0.0)
        df["precipitation_mm"] = df["precipitation_mm"].fillna(0.0)

        logger.info(
            f"✅ Clima obtido: {len(df)} dias | "
            f"Temp média: {df['temp_max'].mean():.1f}°C | "
            f"Dias com chuva: {(df['precipitation_mm'] > 1).sum()}"
        )
        return df

    except httpx.HTTPError as e:
        logger.error(f"❌ Erro ao buscar clima: {e}")
        return _generate_fallback_weather(days_back + forecast_days)
    except Exception as e:
        logger.error(f"❌ Erro inesperado no weather: {e}")
        return _generate_fallback_weather(days_back + forecast_days)


def add_weather_features(
    df: pd.DataFrame, weather_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Faz merge das features de clima no DataFrame principal.

    Args:
        df: DataFrame principal com coluna 'date'
        weather_df: DataFrame de clima (output de fetch_weather_history)

    Returns:
        DataFrame com colunas de clima adicionadas.
    """
    df["date"] = pd.to_datetime(df["date"])
    weather_df["date"] = pd.to_datetime(weather_df["date"])

    # Merge por data
    df = df.merge(
        weather_df[["date", "temp_max", "temp_min", "precipitation_mm", "rain_probability"]],
        on="date",
        how="left",
        suffixes=("", "_weather"),
    )

    # Preencher dias sem dados de clima com a média
    for col in ["temp_max", "temp_min", "precipitation_mm", "rain_probability"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mean())

    logger.info("🌤️ Weather features adicionadas ao DataFrame")
    return df


def _generate_fallback_weather(total_days: int) -> pd.DataFrame:
    """
    Gera dados climáticos simulados caso a API falhe.
    Útil para testes offline.
    """
    import numpy as np

    logger.warning("⚠️ Usando dados climáticos simulados (API offline)")

    today = date.today()
    dates = [today - timedelta(days=total_days - i) for i in range(total_days)]

    return pd.DataFrame({
        "date": pd.to_datetime(dates),
        "temp_max": np.random.normal(28, 5, total_days).round(1),
        "temp_min": np.random.normal(20, 4, total_days).round(1),
        "precipitation_mm": np.maximum(
            np.random.exponential(3, total_days), 0
        ).round(1),
        "rain_probability": np.random.uniform(0, 0.6, total_days).round(2),
    })

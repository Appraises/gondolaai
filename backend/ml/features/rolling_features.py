"""
Rolling Features — Médias móveis e volatilidade.

Captura tendências recentes: "As vendas estão subindo ou caindo?"
A média móvel de 7 dias suaviza o ruído diário e mostra a tendência real.
O desvio padrão indica volatilidade (produto imprevisível vs estável).
"""

import pandas as pd
from loguru import logger


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona médias móveis e desvio padrão ao DataFrame.

    Features geradas:
    - rolling_mean_7d:  Média de vendas dos últimos 7 dias
    - rolling_mean_30d: Média de vendas dos últimos 30 dias
    - rolling_std_7d:   Desvio padrão dos últimos 7 dias (volatilidade)

    Args:
        df: DataFrame com colunas ['product_id', 'date', 'sales_qty']

    Returns:
        DataFrame com as 3 colunas rolling adicionadas.
    """
    df = df.sort_values(["product_id", "date"]).reset_index(drop=True)

    grouped = df.groupby("product_id")["sales_qty"]

    # Média móvel 7 dias (mínimo 1 período para não ser NaN no início)
    df["rolling_mean_7d"] = grouped.transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )

    # Média móvel 30 dias (mínimo 7 períodos)
    df["rolling_mean_30d"] = grouped.transform(
        lambda x: x.rolling(window=30, min_periods=7).mean()
    )

    # Desvio padrão 7 dias (volatilidade)
    df["rolling_std_7d"] = grouped.transform(
        lambda x: x.rolling(window=7, min_periods=2).std()
    )

    # Preencher NaN
    df["rolling_mean_30d"] = df["rolling_mean_30d"].fillna(df["rolling_mean_7d"])
    df["rolling_std_7d"] = df["rolling_std_7d"].fillna(0)

    # Arredondar para 2 casas
    for col in ["rolling_mean_7d", "rolling_mean_30d", "rolling_std_7d"]:
        df[col] = df[col].round(2)

    logger.info("📊 Rolling features adicionadas: rolling_mean_7d, rolling_mean_30d, rolling_std_7d")
    return df

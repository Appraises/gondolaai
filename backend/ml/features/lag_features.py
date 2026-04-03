"""
Lag Features — Vendas de N dias atrás.

Captura: "Quanto desse produto vendeu ontem? E há uma semana?"
Lags de 7 e 14 dias são especialmente úteis porque capturam
o padrão semanal (ex: sábado passado → este sábado).
"""

import pandas as pd
from loguru import logger


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona features de lag (vendas passadas) ao DataFrame.

    Para cada produto, calcula quanto vendeu N dias atrás.

    Features geradas:
    - sales_lag_1d:  Vendas de ontem
    - sales_lag_7d:  Vendas de 7 dias atrás (mesmo dia da semana)
    - sales_lag_14d: Vendas de 14 dias atrás
    - sales_lag_30d: Vendas de 30 dias atrás

    Args:
        df: DataFrame com colunas ['product_id', 'date', 'sales_qty']
            Deve estar ordenado por product_id e date.

    Returns:
        DataFrame com as 4 colunas de lag adicionadas.
    """
    # Garantir ordenação
    df = df.sort_values(["product_id", "date"]).reset_index(drop=True)

    lags = [1, 7, 14, 30]

    for lag in lags:
        col_name = f"sales_lag_{lag}d"
        df[col_name] = (
            df.groupby("product_id")["sales_qty"]
            .shift(lag)
        )
        logger.debug(f"  ✓ {col_name}: {df[col_name].notna().sum()} valores preenchidos")

    # Preencher NaN com 0 (primeiros dias não têm lag)
    lag_cols = [f"sales_lag_{lag}d" for lag in lags]
    df[lag_cols] = df[lag_cols].fillna(0)

    logger.info(f"📊 Lag features adicionadas: {lag_cols}")
    return df

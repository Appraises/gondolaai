"""
Product Features — Características estáticas do produto.

Captura: "É perecível? Está em promoção? Qual a margem?"
Produtos com margem baixa e estoque alto são candidatos a promoção.
"""

from datetime import date

import pandas as pd
from loguru import logger


def add_product_features(
    df: pd.DataFrame,
    products_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Adiciona features do produto ao DataFrame.

    Features geradas:
    - category:         Categoria do produto (label encoded)
    - unit_price:       Preço de venda
    - cost_price:       Preço de custo
    - margin:           Margem = (preço - custo) / preço
    - stock_qty:        Estoque atual
    - days_of_stock:    Dias de estoque restante = estoque / média_7d
    - days_until_expiry: Dias até o vencimento (null se não perecível)

    Args:
        df: DataFrame principal com colunas ['product_id', 'date', 'rolling_mean_7d']
        products_df: DataFrame com dados de produtos do banco

    Returns:
        DataFrame com features de produto adicionadas.
    """
    # Merge com dados do produto
    product_cols = [
        "id", "category", "unit_price", "cost_price",
        "stock_qty", "expiry_date"
    ]
    products_clean = products_df[product_cols].rename(columns={"id": "product_id"})

    # Converter tipos para merge
    products_clean["unit_price"] = products_clean["unit_price"].astype(float)
    products_clean["cost_price"] = products_clean["cost_price"].astype(float)

    df = df.merge(products_clean, on="product_id", how="left", suffixes=("", "_prod"))

    # Margem: (preço - custo) / preço
    df["margin"] = 0.0
    mask = (df["unit_price"] > 0) & (df["cost_price"] > 0)
    df.loc[mask, "margin"] = (
        (df.loc[mask, "unit_price"] - df.loc[mask, "cost_price"])
        / df.loc[mask, "unit_price"]
    ).round(4)

    # Dias de estoque restante
    df["days_of_stock"] = 999.0  # Default alto
    mask = df["rolling_mean_7d"] > 0
    df.loc[mask, "days_of_stock"] = (
        df.loc[mask, "stock_qty"] / df.loc[mask, "rolling_mean_7d"]
    ).round(1)

    # Dias até o vencimento
    df["days_until_expiry"] = None
    mask = df["expiry_date"].notna()
    if mask.any():
        today = pd.Timestamp(date.today())
        df.loc[mask, "days_until_expiry"] = (
            pd.to_datetime(df.loc[mask, "expiry_date"]) - today
        ).dt.days

    # Label encode da categoria (número para o modelo)
    category_map = {
        cat: idx for idx, cat in enumerate(sorted(df["category"].unique()))
    }
    df["category_encoded"] = df["category"].map(category_map)

    # Limpar coluna de expiry_date (não vai pro modelo, só days_until_expiry)
    df = df.drop(columns=["expiry_date"], errors="ignore")

    logger.info(
        f"📦 Product features adicionadas | "
        f"Categorias: {len(category_map)} | "
        f"Margem média: {df['margin'].mean():.1%}"
    )
    return df

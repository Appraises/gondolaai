"""
Calendar Features — Feriados brasileiros e padrões temporais.

Captura: "É véspera de feriado? É semana de pagamento?"
Feriados e fins de semana têm impacto massivo em vendas de supermercado.
"""

from datetime import date, timedelta
from typing import Optional

import holidays
import pandas as pd
from loguru import logger

# Cache dos feriados brasileiros (2024-2028)
_BR_HOLIDAYS = holidays.Brazil(years=range(2024, 2029))


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona features de calendário ao DataFrame.

    Features geradas:
    - day_of_week:       0=Seg, 1=Ter, ..., 6=Dom
    - day_of_month:      1-31
    - week_of_month:     1-5 (captura efeito salário)
    - is_weekend:        True se Sáb ou Dom
    - is_holiday:        True se feriado nacional/estadual
    - days_until_holiday: Dias até o próximo feriado (max 60)

    Args:
        df: DataFrame com coluna 'date' (datetime ou date)

    Returns:
        DataFrame com as 6 colunas de calendário adicionadas.
    """
    # Garantir que date é datetime
    df["date"] = pd.to_datetime(df["date"])

    # Dia da semana (0=Seg ... 6=Dom)
    df["day_of_week"] = df["date"].dt.dayofweek

    # Dia do mês
    df["day_of_month"] = df["date"].dt.day

    # Semana do mês (1-5) — captura efeito do pagamento
    df["week_of_month"] = ((df["date"].dt.day - 1) // 7 + 1).clip(upper=5)

    # É fim de semana?
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # É feriado?
    df["is_holiday"] = df["date"].dt.date.apply(
        lambda d: 1 if d in _BR_HOLIDAYS else 0
    )

    # Dias até o próximo feriado
    df["days_until_holiday"] = df["date"].dt.date.apply(_days_until_next_holiday)

    logger.info(
        f"📅 Calendar features adicionadas | "
        f"Feriados encontrados: {df['is_holiday'].sum()} dias"
    )
    return df


def _days_until_next_holiday(d: date) -> int:
    """Calcula quantos dias faltam para o próximo feriado."""
    for i in range(1, 61):
        future_date = d + timedelta(days=i)
        if future_date in _BR_HOLIDAYS:
            return i
    return 60  # Nenhum feriado nos próximos 60 dias


def get_holiday_name(d: date) -> Optional[str]:
    """Retorna o nome do feriado, ou None se não for feriado."""
    if d in _BR_HOLIDAYS:
        return _BR_HOLIDAYS.get(d)
    return None

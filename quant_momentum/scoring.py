"""Momentum ranking model."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import StrategyConfig
from .indicators import (
    annualized_volatility,
    bollinger_bands,
    max_drawdown,
    moving_average_distance,
    period_return,
    rsi,
)


LOOKBACKS = {
    "return_1m": 21,
    "return_3m": 63,
    "return_6m": 126,
    "return_12m": 252,
}


def build_feature_table(
    prices: pd.DataFrame,
    config: StrategyConfig | None = None,
) -> pd.DataFrame:
    """Create one row of momentum features per ticker."""

    cfg = config or StrategyConfig()
    rows: list[dict[str, float | str]] = []

    for ticker in prices.columns:
        series = prices[ticker].dropna()
        if len(series) < cfg.min_history_days:
            continue

        latest_rsi = rsi(series, cfg.rsi_window).iloc[-1]
        bb = bollinger_bands(series, cfg.bollinger_window, cfg.bollinger_std)
        row: dict[str, float | str] = {
            "ticker": ticker,
            "last_price": float(series.iloc[-1]),
            "rsi": float(latest_rsi),
            "bb_percent_b": float(bb["bb_percent_b"].iloc[-1]),
            "volatility": annualized_volatility(series, cfg.trading_days),
            "max_drawdown": max_drawdown(series),
            "ma_50_distance": moving_average_distance(series, cfg.short_ma),
            "ma_200_distance": moving_average_distance(series, cfg.long_ma),
        }
        for name, lookback in LOOKBACKS.items():
            row[name] = period_return(series, lookback)
        rows.append(row)

    if not rows:
        raise ValueError("No tickers had enough price history to score.")

    return pd.DataFrame(rows)


def score_momentum(features: pd.DataFrame, config: StrategyConfig | None = None) -> pd.DataFrame:
    """Rank tickers and assign explainable trading signals."""

    cfg = config or StrategyConfig()
    scored = features.copy()
    scored["weighted_return"] = (
        0.20 * scored["return_3m"]
        + 0.30 * scored["return_6m"]
        + 0.50 * scored["return_12m"]
    )
    scored["risk_adjusted_momentum"] = scored["weighted_return"] / scored[
        "volatility"
    ].replace(0, np.nan)
    scored["trend_score"] = (
        scored["ma_50_distance"].clip(-0.25, 0.25)
        + scored["ma_200_distance"].clip(-0.35, 0.35)
    )
    scored["technical_penalty"] = np.select(
        [scored["rsi"] > 75, scored["rsi"] < 35, scored["bb_percent_b"] > 1.05],
        [-0.15, -0.05, -0.10],
        default=0.0,
    )
    scored["momentum_score"] = (
        0.35 * percentile_rank(scored["risk_adjusted_momentum"])
        + 0.45 * percentile_rank(scored["weighted_return"])
        + 0.20 * percentile_rank(scored["trend_score"])
        + scored["technical_penalty"]
    )
    scored["momentum_score"] = scored["momentum_score"].round(4)
    scored = scored.sort_values("momentum_score", ascending=False).reset_index(drop=True)
    scored["rank"] = scored.index + 1

    buy_threshold = scored["momentum_score"].quantile(cfg.buy_quantile)
    scored["signal"] = np.where(
        (scored["momentum_score"] >= buy_threshold)
        & (scored["ma_50_distance"] > 0)
        & (scored["ma_200_distance"] > 0)
        & (scored["rsi"].between(40, 75)),
        "BUY",
        np.where(scored["weighted_return"] > 0, "HOLD", "WATCH"),
    )
    return scored


def percentile_rank(values: pd.Series) -> pd.Series:
    """Convert a numeric series to percentile ranks from 0 to 1."""

    return values.rank(pct=True).fillna(0)

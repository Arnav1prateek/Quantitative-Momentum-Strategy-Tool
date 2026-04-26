"""Technical indicators and performance statistics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def daily_returns(prices: pd.Series) -> pd.Series:
    """Return daily percentage changes for a price series."""

    return prices.astype(float).pct_change().replace([np.inf, -np.inf], np.nan)


def period_return(prices: pd.Series, lookback: int) -> float:
    """Return percentage change over a lookback window."""

    clean = prices.dropna()
    if len(clean) <= lookback:
        return np.nan
    return float(clean.iloc[-1] / clean.iloc[-lookback - 1] - 1)


def annualized_volatility(prices: pd.Series, trading_days: int = 252) -> float:
    """Annualized volatility from daily returns."""

    returns = daily_returns(prices).dropna()
    if returns.empty:
        return np.nan
    return float(returns.std(ddof=0) * np.sqrt(trading_days))


def max_drawdown(prices: pd.Series) -> float:
    """Maximum peak-to-trough drawdown."""

    clean = prices.dropna().astype(float)
    if clean.empty:
        return np.nan
    running_max = clean.cummax()
    drawdowns = clean / running_max - 1
    return float(drawdowns.min())


def rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index using Wilder-style exponential smoothing."""

    delta = prices.astype(float).diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    values = 100 - (100 / (1 + rs))
    return values.fillna(50)


def bollinger_bands(
    prices: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> pd.DataFrame:
    """Return middle, upper, lower bands and normalized band position."""

    clean = prices.astype(float)
    middle = clean.rolling(window=window, min_periods=window).mean()
    rolling_std = clean.rolling(window=window, min_periods=window).std(ddof=0)
    upper = middle + num_std * rolling_std
    lower = middle - num_std * rolling_std
    width = (upper - lower).replace(0, np.nan)
    percent_b = (clean - lower) / width
    return pd.DataFrame(
        {
            "bb_middle": middle,
            "bb_upper": upper,
            "bb_lower": lower,
            "bb_percent_b": percent_b,
        }
    )


def moving_average_distance(prices: pd.Series, window: int) -> float:
    """Latest price distance from a moving average."""

    clean = prices.dropna().astype(float)
    if len(clean) < window:
        return np.nan
    ma = clean.rolling(window).mean().iloc[-1]
    return float(clean.iloc[-1] / ma - 1)

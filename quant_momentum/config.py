"""Configuration defaults for the momentum strategy."""

from dataclasses import dataclass


DEFAULT_UNIVERSE = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "JPM",
    "V",
    "UNH",
    "XOM",
    "LLY",
    "AVGO",
    "COST",
    "HD",
    "MA",
]


@dataclass(frozen=True)
class StrategyConfig:
    """Parameters used by the screener."""

    rsi_window: int = 14
    bollinger_window: int = 20
    bollinger_std: float = 2.0
    short_ma: int = 50
    long_ma: int = 200
    trading_days: int = 252
    min_history_days: int = 220
    buy_quantile: float = 0.75

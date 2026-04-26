"""Market data ingestion."""

from __future__ import annotations

import pandas as pd


def fetch_adjusted_close(tickers: list[str], period: str = "2y") -> pd.DataFrame:
    """Download adjusted close prices from Yahoo Finance."""

    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError(
            "yfinance is required for live market data. Install requirements.txt first."
        ) from exc

    if not tickers:
        raise ValueError("At least one ticker is required.")

    raw = yf.download(
        tickers=tickers,
        period=period,
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=True,
    )
    if raw.empty:
        raise RuntimeError("Yahoo Finance returned no data for the requested universe.")

    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" not in raw.columns.get_level_values(0):
            raise RuntimeError("Downloaded data did not include close prices.")
        prices = raw["Close"]
    else:
        prices = raw[["Close"]].rename(columns={"Close": tickers[0]})

    prices = prices.dropna(how="all").sort_index()
    prices.columns = [str(col).upper() for col in prices.columns]
    return prices

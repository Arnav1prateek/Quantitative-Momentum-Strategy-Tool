"""Command-line interface for the momentum screener."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import DEFAULT_UNIVERSE, StrategyConfig
from .data import fetch_adjusted_close
from .report import export_excel_report
from .scoring import build_feature_table, score_momentum


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank equities with a quantitative momentum strategy.")
    parser.add_argument("--tickers", nargs="*", default=DEFAULT_UNIVERSE, help="Ticker symbols to screen.")
    parser.add_argument("--period", default="2y", help="Yahoo Finance period, for example 1y, 2y, 5y.")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top picks to include in the summary.")
    parser.add_argument("--output", default="reports/momentum_report.xlsx", help="Excel report output path.")
    return parser.parse_args()


def run_screen(tickers: list[str], period: str, output: str | Path, top_n: int) -> Path:
    prices = fetch_adjusted_close([ticker.upper() for ticker in tickers], period=period)
    features = build_feature_table(prices, StrategyConfig())
    scored = score_momentum(features, StrategyConfig())
    return export_excel_report(scored, prices, output, top_n=top_n)


def main() -> None:
    args = parse_args()
    report_path = run_screen(args.tickers, args.period, args.output, args.top_n)
    print(f"Momentum report created: {report_path}")


if __name__ == "__main__":
    main()

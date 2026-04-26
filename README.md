# Quantitative Momentum Strategy Tool

A polished Python project for screening equities with a rules-based momentum strategy. The tool pulls market data from Yahoo Finance, computes technical indicators, ranks stocks with a transparent scoring model, and exports an Excel workbook that can be shared with non-technical stakeholders.

## Why this project stands out

- **End-to-end quant workflow:** universe selection, market data ingestion, indicator engineering, ranking, signal generation, and reporting.
- **Transparent methodology:** every score is derived from explainable metrics such as risk-adjusted return, RSI, Bollinger Band position, drawdown, and trend strength.
- **Stakeholder-ready output:** generates an Excel report with summary sheets, signal tables, formatting, and charts.

## Core Features

- Downloads adjusted equity prices using `yfinance`.
- Calculates:
  - 1M, 3M, 6M, and 12M returns
  - annualized volatility
  - Sharpe-like risk-adjusted momentum
  - RSI
  - Bollinger Bands
  - moving-average trend strength
  - maximum drawdown
- Produces ranked buy/hold/watchlist signals.
- Exports an Excel report with conditional formatting and charts.
- Includes a Streamlit dashboard for interactive exploration.
- Ships with tests for the indicator and scoring logic.

## Project Structure

```text
quant-momentum-strategy-tool/
├── quant_momentum/
│   ├── cli.py          # Command-line interface
│   ├── config.py       # Strategy settings and default universe
│   ├── dashboard.py    # Streamlit app
│   ├── data.py         # Yahoo Finance data ingestion
│   ├── indicators.py   # RSI, Bollinger Bands, returns, drawdown
│   ├── report.py       # Excel report generation
│   └── scoring.py      # Ranking and signal generation
├── tests/
│   ├── test_indicators.py
│   └── test_scoring.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Generate a report for a default large-cap universe:

```bash
python -m quant_momentum.cli --period 2y --top-n 10 --output reports/momentum_report.xlsx
```

Run with your own tickers:

```bash
python -m quant_momentum.cli --tickers AAPL MSFT NVDA AMZN META JPM XOM --period 3y
```

Launch the dashboard:

```bash
streamlit run quant_momentum/dashboard.py
```

Run tests:

```bash
pytest
```

## Methodology

The strategy intentionally avoids black-box modeling. Each ticker receives a composite score built from:

- **Return momentum:** weighted 3M, 6M, and 12M returns.
- **Risk control:** penalizes high volatility and large drawdowns.
- **Trend quality:** rewards prices trading above medium and long moving averages.
- **Technical timing:** uses RSI and Bollinger Band position to avoid extremely overbought entries.

Signals are simple and explainable:

- `BUY`: high-ranked stock with positive trend and acceptable RSI.
- `HOLD`: constructive but not top-ranked.
- `WATCH`: weak trend, insufficient momentum, or overextended conditions.

## Notes

This project is for educational and portfolio demonstration purposes. It is not financial advice, and it does not guarantee investment performance.

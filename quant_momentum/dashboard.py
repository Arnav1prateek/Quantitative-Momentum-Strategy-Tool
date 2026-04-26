"""Streamlit dashboard for interactive momentum screening."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from quant_momentum.config import DEFAULT_UNIVERSE, StrategyConfig
from quant_momentum.data import fetch_adjusted_close
from quant_momentum.scoring import build_feature_table, score_momentum


st.set_page_config(page_title="Quant Momentum Screener", layout="wide")


@st.cache_data(show_spinner=False)
def load_screen(tickers: tuple[str, ...], period: str):
    prices = fetch_adjusted_close(list(tickers), period=period)
    features = build_feature_table(prices, StrategyConfig())
    scored = score_momentum(features, StrategyConfig())
    return prices, scored


st.title("Quantitative Momentum Strategy Tool")

with st.sidebar:
    tickers_text = st.text_area("Ticker universe", " ".join(DEFAULT_UNIVERSE), height=140)
    period = st.selectbox("Lookback period", ["1y", "2y", "3y", "5y"], index=1)
    top_n = st.slider("Top picks", min_value=5, max_value=20, value=10)

tickers = tuple(sorted({ticker.strip().upper() for ticker in tickers_text.replace(",", " ").split() if ticker.strip()}))

try:
    prices, scored = load_screen(tickers, period)
except Exception as exc:
    st.error(str(exc))
    st.stop()

top = scored.head(top_n)
buy_count = int(scored["signal"].eq("BUY").sum())

metric_cols = st.columns(4)
metric_cols[0].metric("Universe", len(scored))
metric_cols[1].metric("Buy Signals", buy_count)
metric_cols[2].metric("Best Score", f"{scored['momentum_score'].max():.3f}")
metric_cols[3].metric("Median RSI", f"{scored['rsi'].median():.1f}")

left, right = st.columns([1.15, 0.85])
with left:
    st.subheader("Ranked Momentum Table")
    st.dataframe(
        top[
            [
                "rank",
                "ticker",
                "signal",
                "momentum_score",
                "return_3m",
                "return_6m",
                "return_12m",
                "volatility",
                "rsi",
                "max_drawdown",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

with right:
    fig = px.bar(
        top,
        x="ticker",
        y="momentum_score",
        color="signal",
        title="Top Momentum Scores",
        color_discrete_map={"BUY": "#2E7D32", "HOLD": "#1565C0", "WATCH": "#C62828"},
    )
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

selected = st.selectbox("Inspect price history", top["ticker"].tolist())
price_frame = prices[[selected]].dropna().rename(columns={selected: "Adjusted Close"})
line = px.line(price_frame, y="Adjusted Close", title=f"{selected} Adjusted Close")
line.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20))
st.plotly_chart(line, use_container_width=True)

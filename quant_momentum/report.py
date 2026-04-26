"""Excel report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REPORT_COLUMNS = [
    "rank",
    "ticker",
    "signal",
    "momentum_score",
    "last_price",
    "return_1m",
    "return_3m",
    "return_6m",
    "return_12m",
    "volatility",
    "max_drawdown",
    "rsi",
    "bb_percent_b",
    "ma_50_distance",
    "ma_200_distance",
    "risk_adjusted_momentum",
]


def export_excel_report(
    scored: pd.DataFrame,
    prices: pd.DataFrame,
    output_path: str | Path,
    top_n: int = 10,
) -> Path:
    """Create a formatted Excel workbook."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    report = scored[REPORT_COLUMNS].copy()
    top = report.head(top_n)
    signals = report[report["signal"].eq("BUY")]

    with pd.ExcelWriter(output, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
        top.to_excel(writer, sheet_name="Top Picks", index=False)
        report.to_excel(writer, sheet_name="Full Ranking", index=False)
        signals.to_excel(writer, sheet_name="Buy Signals", index=False)
        prices.tail(252).to_excel(writer, sheet_name="Price History")

        workbook = writer.book
        percent_fmt = workbook.add_format({"num_format": "0.00%"})
        price_fmt = workbook.add_format({"num_format": "$0.00"})
        score_fmt = workbook.add_format({"num_format": "0.000"})
        header_fmt = workbook.add_format(
            {"bold": True, "bg_color": "#17324D", "font_color": "white", "border": 1}
        )
        buy_fmt = workbook.add_format({"bg_color": "#D8EFD3", "font_color": "#145A32"})
        watch_fmt = workbook.add_format({"bg_color": "#FADBD8", "font_color": "#922B21"})

        for sheet_name in ["Top Picks", "Full Ranking", "Buy Signals"]:
            worksheet = writer.sheets[sheet_name]
            frame = top if sheet_name == "Top Picks" else signals if sheet_name == "Buy Signals" else report
            for col_num, column in enumerate(frame.columns):
                worksheet.write(0, col_num, column, header_fmt)
                width = max(12, min(22, len(column) + 3))
                worksheet.set_column(col_num, col_num, width)
            apply_formats(worksheet, frame, percent_fmt, price_fmt, score_fmt, buy_fmt, watch_fmt)

        chart_sheet = writer.sheets["Top Picks"]
        if len(top) > 1:
            chart = workbook.add_chart({"type": "column"})
            chart.add_series(
                {
                    "name": "Momentum Score",
                    "categories": ["Top Picks", 1, 1, len(top), 1],
                    "values": ["Top Picks", 1, 3, len(top), 3],
                    "fill": {"color": "#2F75B5"},
                }
            )
            chart.set_title({"name": "Top Momentum Scores"})
            chart.set_y_axis({"name": "Score"})
            chart.set_legend({"none": True})
            chart_sheet.insert_chart("R2", chart, {"x_scale": 1.25, "y_scale": 1.15})

    return output


def apply_formats(
    worksheet,
    frame: pd.DataFrame,
    percent_fmt,
    price_fmt,
    score_fmt,
    buy_fmt,
    watch_fmt,
) -> None:
    """Apply worksheet-level number and signal formatting."""

    if frame.empty:
        return

    columns = list(frame.columns)
    percent_columns = [
        "return_1m",
        "return_3m",
        "return_6m",
        "return_12m",
        "volatility",
        "max_drawdown",
        "bb_percent_b",
        "ma_50_distance",
        "ma_200_distance",
        "risk_adjusted_momentum",
    ]
    for column in percent_columns:
        if column in columns:
            idx = columns.index(column)
            worksheet.set_column(idx, idx, 14, percent_fmt)
    if "last_price" in columns:
        idx = columns.index("last_price")
        worksheet.set_column(idx, idx, 12, price_fmt)
    if "momentum_score" in columns:
        idx = columns.index("momentum_score")
        worksheet.set_column(idx, idx, 16, score_fmt)
    if "signal" in columns:
        idx = columns.index("signal")
        worksheet.conditional_format(1, idx, len(frame), idx, {"type": "text", "criteria": "containing", "value": "BUY", "format": buy_fmt})
        worksheet.conditional_format(1, idx, len(frame), idx, {"type": "text", "criteria": "containing", "value": "WATCH", "format": watch_fmt})

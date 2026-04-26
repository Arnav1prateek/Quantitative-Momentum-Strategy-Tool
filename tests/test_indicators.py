import pandas as pd

from quant_momentum.indicators import bollinger_bands, max_drawdown, period_return, rsi


def test_period_return_uses_requested_lookback():
    prices = pd.Series([100, 105, 110, 121], dtype=float)

    assert period_return(prices, 2) == 121 / 105 - 1


def test_rsi_stays_in_valid_range():
    prices = pd.Series([100, 101, 102, 101, 103, 104, 102, 105, 106, 108, 107, 109, 111, 110, 112, 113])

    result = rsi(prices)

    assert result.between(0, 100).all()


def test_bollinger_band_position_is_calculated():
    prices = pd.Series(range(1, 31), dtype=float)

    bands = bollinger_bands(prices, window=20)

    assert {"bb_middle", "bb_upper", "bb_lower", "bb_percent_b"} <= set(bands.columns)
    assert bands["bb_percent_b"].dropna().iloc[-1] > 0.5


def test_max_drawdown_detects_largest_loss():
    prices = pd.Series([100, 120, 90, 130], dtype=float)

    assert max_drawdown(prices) == -0.25

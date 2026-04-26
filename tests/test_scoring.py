import pandas as pd

from quant_momentum.config import StrategyConfig
from quant_momentum.scoring import build_feature_table, score_momentum


def make_prices() -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=280, freq="B")
    return pd.DataFrame(
        {
            "AAA": [100 + i * 0.35 for i in range(280)],
            "BBB": [100 + i * 0.08 for i in range(280)],
            "CCC": [120 - i * 0.05 for i in range(280)],
        },
        index=index,
    )


def test_scoring_ranks_stronger_momentum_higher():
    cfg = StrategyConfig(min_history_days=200)
    features = build_feature_table(make_prices(), cfg)
    scored = score_momentum(features, cfg)

    assert scored.iloc[0]["ticker"] == "AAA"
    assert scored.iloc[0]["rank"] == 1
    assert set(scored["signal"]) <= {"BUY", "HOLD", "WATCH"}

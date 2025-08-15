import numpy as np
import pandas as pd
from app.copula import gaussian_copula_joint_overprob


def test_copula_shapes():
    df = pd.DataFrame({
        "pts": np.random.poisson(25, size=200),
        "reb": np.random.poisson(8, size=200),
        "ast": np.random.poisson(6, size=200),
    })
    legs = [
        {"player_id": 1, "prop": "pts", "threshold": 20, "op": ">="},
        {"player_id": 1, "prop": "reb", "threshold": 5, "op": ">="},
        {"player_id": 1, "prop": "ast", "threshold": 4, "op": ">="},
    ]
    joint, marginals, taus = gaussian_copula_joint_overprob(df, legs, n_samples=5000)
    assert 0.0 <= joint <= 1.0
    assert len(marginals) == 3
    assert len(taus) == 3 and len(taus[0]) == 3
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import norm, kendalltau

# Gaussian copula utilities

def ecdf_inverse_quantile(x: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Inverse ECDF (quantile) via interpolation. x must be 1D sample.
    u in (0,1). Returns quantiles matching empirical distribution of x.
    """
    xs = np.sort(x)
    n = len(xs)
    ranks = np.linspace(1.0/(n+1), n/(n+1), n)
    return np.interp(u, ranks, xs)


def gaussian_copula_joint_overprob(df: pd.DataFrame, legs: list[dict], n_samples: int = 20000) -> tuple[float, list[float], list[list[float]]]:
    """Compute joint probability that each prop exceeds its threshold using a Gaussian copula.
    - df: DataFrame with columns for each prop used in legs (aligned by game_id).
    - legs: [{player_id, prop, threshold, op}] with op assumed '>=/over'.
    Returns: (joint_prob, marginals, kendall_tau_matrix)
    """
    props = [leg["prop"] for leg in legs]
    X = df[props].astype(float).to_numpy()
    if X.size == 0 or X.shape[0] < 5:
        # Not enough data; fall back to independence approximation using marginals from df
        marginals = []
        for i, leg in enumerate(legs):
            xi = df[leg["prop"].strip()].values.astype(float)
            marginals.append(float((xi >= float(leg["threshold"])) .mean()) if len(xi) else 0.0)
        joint_indep = float(np.prod(marginals))
        taus = [[1.0 if i==j else 0.0 for j in range(len(legs))] for i in range(len(legs))]
        return joint_indep, marginals, taus

    # Transform to Gaussian space via probability integral transform
    Ucols = []
    for j, prop in enumerate(props):
        x = X[:, j]
        ranks = pd.Series(x).rank(method="average").to_numpy()
        U = ranks / (len(x) + 1.0)
        Ucols.append(U)
    U = np.column_stack(Ucols)
    Z = norm.ppf(U)

    # Estimate correlation matrix
    R = np.corrcoef(Z, rowvar=False)
    # Fix numerical issues
    eigvals, eigvecs = np.linalg.eigh(R)
    eigvals_clipped = np.clip(eigvals, 1e-6, None)
    R = (eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T)

    # Compute Kendall's tau matrix from df for reporting
    taus = np.eye(len(props)).tolist()
    for i in range(len(props)):
        for j in range(i+1, len(props)):
            tau, _ = kendalltau(df[props[i]], df[props[j]])
            taus[i][j] = taus[j][i] = float(0.0 if tau is None or np.isnan(tau) else tau)

    # Monte Carlo sampling from MVN(0, R)
    L = np.linalg.cholesky(R)
    Zs = np.random.normal(size=(n_samples, len(props))) @ L.T
    Us = norm.cdf(Zs)

    # Map uniform to empirical quantiles, then check thresholds
    meets = np.ones(n_samples, dtype=bool)
    marginals = []
    for j, leg in enumerate(legs):
        x = X[:, j]
        q = ecdf_inverse_quantile(x, Us[:, j])
        th = float(leg["threshold"])  # over/>= assumed
        mj = float((x >= th).mean())
        marginals.append(mj)
        meets &= (q >= th)

    joint = float(meets.mean())
    return joint, marginals, taus
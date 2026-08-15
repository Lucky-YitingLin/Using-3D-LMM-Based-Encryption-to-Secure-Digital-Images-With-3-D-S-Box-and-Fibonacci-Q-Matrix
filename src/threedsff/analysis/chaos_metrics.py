"""Dynamical diagnostics used in paper Section III-B."""

from __future__ import annotations

import math
import numpy as np

from ..chaos import lmm_step
from ..config import LMMParameters


def jacobian_3d_lmm(x: float, y: float, z: float, p: LMMParameters) -> np.ndarray:
    """Analytic Jacobian of paper Eq. (1), used for Lyapunov estimation."""

    ax = p.a * p.d * (-math.sin(x * (1.0 - x))) * (1.0 - 2.0 * x)
    ay = p.a * p.d * (-math.sin(y * (1.0 - y))) * (1.0 - 2.0 * y)
    az = p.a * p.d * (-math.sin(z * (1.0 - z))) * (1.0 - 2.0 * z)
    bx = p.a * p.b * math.pi * math.cos(math.pi * x)
    by = p.a * p.b * math.pi * math.cos(math.pi * y)
    bz = p.a * p.b * math.pi * math.cos(math.pi * z)
    return np.array([[ax, 0.0, bz], [bx, ay, 0.0], [0.0, by, az]], dtype=np.float64)


def lyapunov_exponents(
    *,
    x0: float = 0.1,
    y0: float = 0.2,
    z0: float = 0.3,
    params: LMMParameters = LMMParameters(),
    transient: int = 500,
    iterations: int = 3000,
) -> np.ndarray:
    """Estimate all three Lyapunov exponents with the QR/Benettin method."""

    x, y, z = x0, y0, z0
    for _ in range(transient):
        x, y, z = lmm_step(x, y, z, params)
    q = np.eye(3, dtype=np.float64)
    accum = np.zeros(3, dtype=np.float64)
    for _ in range(iterations):
        j = jacobian_3d_lmm(x, y, z, params)
        q, r = np.linalg.qr(j @ q)
        accum += np.log(np.maximum(np.abs(np.diag(r)), np.finfo(float).tiny))
        x, y, z = lmm_step(x, y, z, params)
    return accum / iterations


def gottwald_melbourne_k(phi: np.ndarray, *, samples: int = 32, seed: int = 0) -> float:
    """Estimate the Gottwald-Melbourne 0-1 chaos statistic K.

    This is a compact, reproducible implementation suitable for diagnostic
    comparison.  The paper does not state the exact c-values, regression range,
    or preprocessing used for Fig. 7, so bit-for-bit figure reproduction is not
    claimed.
    """

    phi = np.asarray(phi, dtype=np.float64).reshape(-1)
    n = phi.size
    if n < 200:
        raise ValueError("0-1 test needs a reasonably long sequence")
    rng = np.random.default_rng(seed)
    cs = rng.uniform(math.pi / 5, 4 * math.pi / 5, size=samples)
    max_lag = max(10, n // 10)
    lags = np.arange(1, max_lag + 1, dtype=np.float64)
    ks = []
    idx = np.arange(1, n + 1, dtype=np.float64)
    for c in cs:
        p = np.cumsum(phi * np.cos(idx * c))
        q = np.cumsum(phi * np.sin(idx * c))
        msd = np.empty(max_lag, dtype=np.float64)
        for lag in range(1, max_lag + 1):
            dp = p[lag:] - p[:-lag]
            dq = q[lag:] - q[:-lag]
            msd[lag - 1] = np.mean(dp * dp + dq * dq)
        ks.append(np.corrcoef(lags, msd)[0, 1])
    return float(np.median(ks))


def pq_trajectory(phi: np.ndarray, c: float = 1.7) -> tuple[np.ndarray, np.ndarray]:
    """Map a scalar time series to the p-q plane for a Fig. 7 style plot."""

    phi = np.asarray(phi, dtype=np.float64).reshape(-1)
    idx = np.arange(1, phi.size + 1, dtype=np.float64)
    p = np.cumsum(phi * np.cos(idx * c))
    q = np.cumsum(phi * np.sin(idx * c))
    return p, q

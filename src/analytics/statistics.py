"""
Statistical utilities: Wilson score confidence intervals and bootstrap estimators.
"""

import math
from typing import Tuple
from scipy import stats
import numpy as np


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculates Wilson score confidence interval for a binomial proportion.
    Robust for small sample sizes and proportions near 0 or 1.
    """
    if total <= 0:
        return 0.0, 0.0

    p_hat = successes / total
    z = stats.norm.ppf(1 - (1 - confidence) / 2)

    z2 = z ** 2
    denominator = 1 + z2 / total
    centre_adjusted_probability = p_hat + z2 / (2 * total)
    adjusted_std_dev = math.sqrt((p_hat * (1 - p_hat) + z2 / (4 * total)) / total)
    raw_lower = (centre_adjusted_probability - z * adjusted_std_dev) / denominator
    raw_upper = (centre_adjusted_probability + z * adjusted_std_dev) / denominator

    if successes <= 0:
        lower = 0.0
    else:
        lower = max(0.0, float(raw_lower))
        if lower < 1e-9:
            lower = 0.0

    if successes >= total:
        upper = 1.0
    else:
        upper = min(1.0, float(raw_upper))

    return float(lower), float(upper)


def bootstrap_confidence_interval(data: np.ndarray, num_resamples: int = 1000, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculates non-parametric bootstrap confidence interval for the mean.
    """
    if len(data) == 0:
        return 0.0, 0.0
    if len(data) == 1:
        val = float(data[0])
        return val, val

    boot_means = np.empty(num_resamples)
    n = len(data)
    for i in range(num_resamples):
        sample = np.random.choice(data, size=n, replace=True)
        boot_means[i] = np.mean(sample)

    alpha = (1.0 - confidence) / 2.0
    lower = np.percentile(boot_means, 100 * alpha)
    upper = np.percentile(boot_means, 100 * (1.0 - alpha))
    return float(lower), float(upper)

"""
Time-series proxy forecasting and trend estimation for P&G Need Share.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from src.logging import get_logger

logger = get_logger("forecast_model")


def forecast_need_share_trend(
    df_need_share: pd.DataFrame,
    periods_ahead: int = 2
) -> pd.DataFrame:
    """
    Computes linear trend forecast for P&G Need Share by proxy period.
    """
    if "proxy_period" not in df_need_share.columns or "pg_need_share" not in df_need_share.columns:
        return df_need_share

    # Overall period trend
    period_avg = df_need_share.groupby("proxy_period")["pg_need_share"].mean().reset_index()
    period_avg["period_idx"] = np.arange(len(period_avg))

    if len(period_avg) < 2:
        return period_avg

    # Fit linear slope
    x = period_avg["period_idx"].values
    y = period_avg["pg_need_share"].values
    slope, intercept = np.polyfit(x, y, 1)

    future_periods = []
    last_idx = x[-1]
    for i in range(1, periods_ahead + 1):
        f_idx = last_idx + i
        f_val = max(0.0, min(1.0, float(slope * f_idx + intercept)))
        future_periods.append({
            "proxy_period": f"Forecast_Period_{i}",
            "pg_need_share": round(f_val, 4),
            "period_idx": f_idx,
            "is_forecast": True,
        })

    period_avg["is_forecast"] = False
    df_forecast = pd.concat([period_avg, pd.DataFrame(future_periods)], ignore_index=True)
    logger.info(f"Generated {periods_ahead}-period trend forecast (Slope={slope:.4f}).")
    return df_forecast

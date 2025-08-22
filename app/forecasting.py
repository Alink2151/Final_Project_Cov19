from __future__ import annotations
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def forecast_cases(df: pd.DataFrame, horizon_days: int = 14) -> pd.DataFrame:
	series = df.set_index("DATE")["CASES"].asfreq("D").fillna(0)
	model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(0, 1, 1, 7), enforce_stationarity=False, enforce_invertibility=False)
	fit = model.fit(disp=False)
	pred = fit.get_forecast(steps=horizon_days)
	pred_df = pred.summary_frame()
	pred_df = pred_df.rename(columns={"mean": "forecast", "mean_ci_lower": "lower", "mean_ci_upper": "upper"})
	pred_df.index.name = "DATE"
	return pred_df.reset_index()[["DATE", "forecast", "lower", "upper"]]
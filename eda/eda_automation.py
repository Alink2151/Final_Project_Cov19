from __future__ import annotations
import os
import pandas as pd
from pathlib import Path
from app.config import SnowflakeConfig
from app.snowflake_client import SnowflakeClient


OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def profile_table(client: SnowflakeClient, view_name: str) -> dict:
	df = client.fetch_df(f"SELECT * FROM {view_name} LIMIT 100000")
	profile = {
		"row_count": len(df),
		"columns": list(df.columns),
		"null_counts": df.isna().sum().to_dict(),
		"dtypes": {c: str(t) for c, t in df.dtypes.items()},
	}
	return profile


def run():
	cfg = SnowflakeConfig()
	client = SnowflakeClient(cfg)

	views = [
		"COVID_APP.PUBLIC.V_JHU_GLOBAL",
		"COVID_APP.PUBLIC.V_JHU_US",
	]

	results = {}
	for v in views:
		results[v] = profile_table(client, v)

	pd.DataFrame.from_dict(results, orient="index").to_json(OUTPUT_DIR / "profiles.json", orient="index")

	# Simple aggregated metrics
	df_global = client.fetch_df(
		"""
		SELECT COUNTRY_REGION, DATE,
			SUM(NEW_CONFIRMED) AS NEW_CASES,
			SUM(NEW_DEATHS) AS NEW_DEATHS
		FROM COVID_APP.PUBLIC.V_JHU_GLOBAL
		GROUP BY COUNTRY_REGION, DATE
		"""
	)
	df_global.to_csv(OUTPUT_DIR / "global_timeseries.csv", index=False)

	with open(OUTPUT_DIR / "summary.html", "w", encoding="utf-8") as f:
		f.write("<h1>EDA Summary</h1>")
		f.write("<p>Generated profiles and aggregated time series.</p>")
		f.write("<ul>")
		for v in views:
			f.write(f"<li>Profiled: {v}</li>")
		f.write("</ul>")


if __name__ == "__main__":
	run()
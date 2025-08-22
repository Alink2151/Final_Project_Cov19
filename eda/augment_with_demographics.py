from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
from app.config import SnowflakeConfig
from app.snowflake_client import SnowflakeClient

DATA_PATH = Path(os.getenv("DEMOGRAPHICS_CSV", "data/us_states_demographics.csv"))
TABLE_NAME = "US_STATE_DEMOGRAPHICS"


def load_csv_to_snowflake(csv_path: Path, client: SnowflakeClient):
	if not csv_path.exists():
		raise FileNotFoundError(f"CSV not found: {csv_path}")
	df = pd.read_csv(csv_path)
	client.execute(f"CREATE OR REPLACE TABLE {TABLE_NAME} (STATE STRING, POPULATION NUMBER, MEDIAN_AGE FLOAT, POVERTY_RATE FLOAT, INCOME FLOAT)")
	with client._connection() as conn:  # type: ignore[attr-defined]
		write_pandas(conn, df, TABLE_NAME)


def create_join_view(client: SnowflakeClient):
	sql = f"""
	CREATE OR REPLACE VIEW V_JHU_US_WITH_DEMOGRAPHICS AS
	SELECT j.PROVINCE_STATE AS STATE, j.DATE, j.NEW_CONFIRMED, j.NEW_DEATHS,
	       d.POPULATION, d.MEDIAN_AGE, d.POVERTY_RATE, d.INCOME
	FROM V_JHU_US j
	LEFT JOIN {TABLE_NAME} d
	  ON UPPER(d.STATE) = UPPER(j.PROVINCE_STATE);
	"""
	client.execute(sql)


def run():
	cfg = SnowflakeConfig()
	client = SnowflakeClient(cfg)
	load_csv_to_snowflake(DATA_PATH, client)
	create_join_view(client)
	print("Augmentation complete: V_JHU_US_WITH_DEMOGRAPHICS created")


if __name__ == "__main__":
	run()
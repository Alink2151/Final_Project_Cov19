from __future__ import annotations
import pandas as pd


def to_records(df: pd.DataFrame) -> list[dict]:
	if df is None:
		return []
	return df.where(pd.notnull(df), None).to_dict(orient="records")
from __future__ import annotations
import snowflake.connector
import pandas as pd
from contextlib import contextmanager
from .config import SnowflakeConfig


class SnowflakeClient:
	def __init__(self, config: SnowflakeConfig):
		self._config = config

	@contextmanager
	def _connection(self):
		conn = snowflake.connector.connect(
			account=self._config.account,
			user=self._config.user,
			password=self._config.password,
			role=self._config.role,
			warehouse=self._config.warehouse,
			database=self._config.database,
			schema=self._config.schema,
		)
		try:
			yield conn
		finally:
			conn.close()

	def fetch_df(self, sql: str, params: dict | None = None) -> pd.DataFrame:
		with self._connection() as conn:
			cursor = conn.cursor()
			try:
				cursor.execute(sql, params or {})
				return cursor.fetch_pandas_all()
			finally:
				cursor.close()

	def execute(self, sql: str, params: dict | None = None) -> None:
		with self._connection() as conn:
			cursor = conn.cursor()
			try:
				cursor.execute(sql, params or {})
			finally:
				cursor.close()
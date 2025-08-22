from __future__ import annotations
from flask import Blueprint, request, jsonify
from .snowflake_client import SnowflakeClient
from .mongo_client import MongoService
from .cache import Cache
from .utils import to_records
from .forecasting import forecast_cases
from .clustering import cluster_regions


api_bp = Blueprint("api", __name__)


def init_routes(snow: SnowflakeClient, mongo: MongoService, cache: Cache):
	@api_bp.get("/health")
	def health():
		return {"status": "ok"}

	@api_bp.get("/timeseries")
	def timeseries():
		region = request.args.get("region", "US")
		country = request.args.get("country", "United States")
		sql = """
		SELECT DATE, SUM(NEW_CONFIRMED) AS CASES
		FROM COVID_APP.PUBLIC.V_JHU_GLOBAL
		WHERE COUNTRY_REGION = %(country)s
		GROUP BY DATE
		ORDER BY DATE
		"""
		key = {"endpoint": "timeseries", "country": country}
		data = cache.get_or_set("sql", key, 3600, lambda: to_records(snow.fetch_df(sql, {"country": country})))
		return jsonify(data)

	@api_bp.get("/forecast")
	def forecast():
		country = request.args.get("country", "United States")
		sql = """
		SELECT DATE, SUM(NEW_CONFIRMED) AS CASES
		FROM COVID_APP.PUBLIC.V_JHU_GLOBAL
		WHERE COUNTRY_REGION = %(country)s
		GROUP BY DATE
		ORDER BY DATE
		"""
		df = snow.fetch_df(sql, {"country": country})
		pred = forecast_cases(df, horizon_days=int(request.args.get("horizon", 14)))
		return jsonify(to_records(pred))

	@api_bp.get("/clusters")
	def clusters():
		sql = """
		SELECT COUNTRY_REGION, SUM(NEW_CONFIRMED) AS total_cases,
			SUM(NEW_DEATHS) AS total_deaths,
			AVG(NEW_CONFIRMED) AS avg_daily_cases
		FROM COVID_APP.PUBLIC.V_JHU_GLOBAL
		GROUP BY COUNTRY_REGION
		"""
		df = snow.fetch_df(sql)
		df["cases_per_100k"] = df["total_cases"]
		df["deaths_per_100k"] = df["total_deaths"]
		df["growth_rate"] = df["avg_daily_cases"]
		clustered = cluster_regions(df, n_clusters=int(request.args.get("k", 5)))
		return jsonify(to_records(clustered))

	@api_bp.get("/pattern")
	def pattern():
		country = request.args.get("country", "United States")
		sql = """
		SELECT * FROM COVID_APP.PUBLIC.V_PATTERN_SURGE WHERE COUNTRY_REGION = %(country)s
		"""
		return jsonify(to_records(snow.fetch_df(sql, {"country": country})))

	@api_bp.post("/comments")
	def post_comment():
		payload = request.get_json(force=True) or {}
		comment_id = mongo.add_comment({
			"country": payload.get("country"),
			"region": payload.get("region"),
			"date": payload.get("date"),
			"text": payload.get("text"),
		})
		return {"inserted_id": comment_id}

	@api_bp.get("/comments")
	def get_comments():
		country = request.args.get("country")
		region = request.args.get("region")
		filter_query = {k: v for k, v in {"country": country, "region": region}.items() if v}
		return jsonify(mongo.list_comments(filter_query))
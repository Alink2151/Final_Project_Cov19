import os
from dataclasses import dataclass


def get_env(name: str, default: str | None = None) -> str:
	value = os.getenv(name, default)
	if value is None:
		raise RuntimeError(f"Missing required environment variable: {name}")
	return value


@dataclass
class SnowflakeConfig:
	account: str = get_env("SNOWFLAKE_ACCOUNT")
	user: str = get_env("SNOWFLAKE_USER")
	password: str = get_env("SNOWFLAKE_PASSWORD")
	role: str = get_env("SNOWFLAKE_ROLE", "SYSADMIN")
	warehouse: str = get_env("SNOWFLAKE_WAREHOUSE", "COVID_WH")
	database: str = get_env("SNOWFLAKE_DATABASE", "COVID_APP")
	schema: str = get_env("SNOWFLAKE_SCHEMA", "PUBLIC")


@dataclass
class MongoConfig:
	uri: str = get_env("MONGO_URI", "mongodb://localhost:27017")
	database: str = get_env("MONGO_DB", "covid_app")


@dataclass
class RedisConfig:
	url: str = get_env("REDIS_URL", "redis://localhost:6379/0")


@dataclass
class AppConfig:
	secret_key: str = get_env("SECRET_KEY", "change-me")
	api_host: str = get_env("API_HOST", "0.0.0.0")
	api_port: int = int(get_env("API_PORT", "8000"))
	dash_host: str = get_env("DASH_HOST", "0.0.0.0")
	dash_port: int = int(get_env("DASH_PORT", "8050"))
	flask_env: str = get_env("FLASK_ENV", "development")
	flask_debug: bool = get_env("FLASK_DEBUG", "0") == "1"
	student_name: str = get_env("STUDENT_NAME", "Your Name Here")
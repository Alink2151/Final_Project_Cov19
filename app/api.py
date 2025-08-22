from __future__ import annotations
from flask import Flask
from flask_cors import CORS
from .config import SnowflakeConfig, MongoConfig, RedisConfig, AppConfig
from .snowflake_client import SnowflakeClient
from .mongo_client import MongoService
from .cache import Cache
from .routes import api_bp, init_routes


snow_cfg = SnowflakeConfig()
mongo_cfg = MongoConfig()
redis_cfg = RedisConfig()
app_cfg = AppConfig()

snow_client = SnowflakeClient(snow_cfg)
mongo_service = MongoService(mongo_cfg)
cache = Cache(redis_cfg)

init_routes(snow_client, mongo_service, cache)

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = app_cfg.secret_key
app.register_blueprint(api_bp, url_prefix="/api")


if __name__ == "__main__":
	app.run(host=app_cfg.api_host, port=app_cfg.api_port, debug=app_cfg.flask_debug)
from __future__ import annotations
import hashlib
import json
from typing import Callable, Any
import redis
from .config import RedisConfig


class Cache:
	def __init__(self, config: RedisConfig):
		self._redis = redis.from_url(config.url)

	def _key(self, namespace: str, key_obj: Any) -> str:
		digest = hashlib.sha1(json.dumps(key_obj, sort_keys=True, default=str).encode()).hexdigest()
		return f"covid:{namespace}:{digest}"

	def get_or_set(self, namespace: str, key_obj: Any, ttl_seconds: int, producer: Callable[[], Any]):
		key = self._key(namespace, key_obj)
		try:
			cached = self._redis.get(key)
			if cached is not None:
				return json.loads(cached)
		except Exception:
			# Redis unavailable: compute fresh value and return without caching
			return producer()
		value = producer()
		try:
			self._redis.setex(key, ttl_seconds, json.dumps(value, default=str))
		except Exception:
			pass
		return value
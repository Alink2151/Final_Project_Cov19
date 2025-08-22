from __future__ import annotations
from pymongo import MongoClient
from .config import MongoConfig


class MongoService:
	def __init__(self, config: MongoConfig):
		self._client = MongoClient(config.uri)
		self._db = self._client[config.database]

	@property
	def comments(self):
		return self._db["comments"]

	def add_comment(self, payload: dict) -> str:
		result = self.comments.insert_one(payload)
		return str(result.inserted_id)

	def list_comments(self, filter_query: dict, limit: int = 100):
		return list(self.comments.find(filter_query).limit(limit))
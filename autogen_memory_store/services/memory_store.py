import base64
import json
from dataclasses import dataclass
from typing import Any, Mapping

from azure.identity import DefaultAzureCredential
from lagom.environment import Env
from redis import Redis

from autogen_memory_store.models.chat_message import ChatMessage
from autogen_memory_store.protocols.i_memory_store import IMemoryStore

# this can be redis, for simpification we use file system


class MemoryStoreEnv(Env):
    redis_scope: str
    redis_host: str
    redis_port: int
    redis_key: str | None = None


def extract_username_from_token(token):
    parts = token.split(".")
    base64_str = parts[1]

    if len(base64_str) % 4 == 2:
        base64_str += "=="
    elif len(base64_str) % 4 == 3:
        base64_str += "="

    json_bytes = base64.b64decode(base64_str)
    json_str = json_bytes.decode("utf-8")
    jwt = json.loads(json_str)

    return jwt["oid"]


@dataclass
class MemoryStore(IMemoryStore):
    env: MemoryStoreEnv

    def __post_init__(self):
        params = {
            "host": self.env.redis_host,
            "port": self.env.redis_port,
            "ssl": True,
        }

        if self.env.redis_key is None:
            cred = DefaultAzureCredential()
            token = cred.get_token(self.env.redis_scope)

            params["username"] = extract_username_from_token(token.token)
            params["password"] = token.token
        else:
            params["password"] = self.env.redis_key

        self.redis_client = Redis(**params)

    def read_history(self, key: str) -> list[ChatMessage]:
        data = self.redis_client.get(f"{key}:history")

        if data:
            return [ChatMessage(**x) for x in json.loads(data)]  # type: ignore
        return []

    def write_history(self, key: str, history: list[ChatMessage]) -> None:
        all_history = self.read_history(key) + history
        self.redis_client.set(
            f"{key}:history", json.dumps([msg.model_dump() for msg in all_history])
        )

    def read_graph_memory(self, key: str) -> Mapping[str, Any] | None:
        data = self.redis_client.get(f"{key}:memory")
        if not data:
            return None
        return json.loads(data)  # type: ignore

    def write_graph_memory(self, key: str, state: Mapping[str, Any]) -> None:
        self.redis_client.set(f"{key}:memory", json.dumps(state))

    def put(
        self, key: str, messages: list[ChatMessage], state: Mapping[str, Any]
    ) -> None:
        self.write_history(key, messages)
        self.write_graph_memory(key, state)

    def restore(self, key: str) -> Mapping[str, Any] | None:
        return self.read_graph_memory(key)

    def get_chat_history(self, key: str) -> list[ChatMessage]:
        return self.read_history(key)

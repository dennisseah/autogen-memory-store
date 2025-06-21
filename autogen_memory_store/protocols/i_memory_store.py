from typing import Any, Mapping, Protocol

from autogen_memory_store.models.chat_message import ChatMessage


class IMemoryStore(Protocol):
    def put(
        self, key: str, messages: list[ChatMessage], state: Mapping[str, Any]
    ) -> None:
        """
        Store a value in the memory store with the given key.

        :param key: The key under which to store the value.
        :param messages: The list of ChatMessage instances to store.
        :param state: graph state.
        """
        ...

    def restore(self, key: str) -> Mapping[str, Any] | None:
        """
        Restore a value from the memory store with the given key.

        :param key: The key under which the value is stored.
        :return: restored memory.
        """
        ...

    def get_chat_history(self, key: str) -> list[ChatMessage]:
        """
        Read the history of messages stored under the given key.

        :param key: The key under which the history is stored.
        :return: A list of ChatMessage instances representing the history.
        """
        ...

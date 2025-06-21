from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from autogen_memory_store.hosting import container
from autogen_memory_store.models.chat_message import ChatMessage
from autogen_memory_store.protocols.i_azure_openai_service import IAzureOpenAIService
from autogen_memory_store.protocols.i_memory_store import IMemoryStore

memory_store = container[IMemoryStore]


async def generate(
    user_message: str, state: Mapping[str, Any] | None
) -> tuple[Mapping, str]:
    model_client = container[IAzureOpenAIService].get_model()

    assistant_agent = AssistantAgent(
        name="assistant_agent",
        system_message="You are a helpful assistant. You may be asked to generate a random number.",  # noqa E501
        model_client=model_client,
    )
    if state:
        print("Restoring state for the assistant agent.")
        await assistant_agent.load_state(state)  # type:
    else:
        print("No state found, starting fresh.")

    response = await assistant_agent.on_messages(
        [TextMessage(content=user_message, source="user")],
        CancellationToken(),
    )

    new_state = await assistant_agent.save_state()
    await model_client.close()
    return new_state, response.chat_message.content  # type: ignore


async def serve(thread_id: str, input_message: str) -> str:
    # capture the user input in history
    history = [
        ChatMessage(
            message=input_message,
            role="user",
            domain="demo",
            ts=datetime.now(timezone.utc).timestamp(),
        )
    ]

    state, response = await generate(
        user_message=input_message,
        state=memory_store.restore(thread_id),
    )

    history.append(
        ChatMessage(
            message=response,
            role="ai",
            domain="demo",
            ts=datetime.now(timezone.utc).timestamp(),
        )
    )

    memory_store.put(key=thread_id, state=state, messages=history)
    return response

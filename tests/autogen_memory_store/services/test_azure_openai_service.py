from typing import Callable
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from autogen_memory_store.services.azure_openai_service import (
    AzureOpenAIService,
)


@pytest.fixture
def fn_mock_service(mocker: MockerFixture) -> Callable[[bool], AzureOpenAIService]:
    def wrapper(with_api_key: bool) -> AzureOpenAIService:
        mock_cred = MagicMock()
        mock_cred.get_token.return_value = MagicMock(
            token="mock_token",
            scope="https://example.com/.default",
        )
        mocker.patch(
            "autogen_memory_store.services.azure_openai_service.DefaultAzureCredential",
            return_value=mock_cred,
        )

        env = MagicMock()
        if not with_api_key:
            env.azure_openai_api_key = None
        svc = AzureOpenAIService(env=env)  # type: ignore
        return svc

    return wrapper


def test_get_model(
    fn_mock_service: Callable[[bool], AzureOpenAIService], mocker: MockerFixture
):
    patched_azure_openai = mocker.patch(
        "autogen_memory_store.services.azure_openai_service.AzureOpenAIChatCompletionClient",
        autospec=True,
    )

    mock_service = fn_mock_service(with_api_key=True)  # type: ignore
    assert mock_service.get_model() is not None
    patched_azure_openai.assert_called_once()


def test_get_model_without_aoi_key(
    fn_mock_service: Callable[[bool], AzureOpenAIService], mocker: MockerFixture
):
    patched_azure_openai = mocker.patch(
        "autogen_memory_store.services.azure_openai_service.AzureOpenAIChatCompletionClient",
        autospec=True,
    )

    mock_service = fn_mock_service(with_api_key=False)  # type: ignore
    assert mock_service.get_model() is not None
    patched_azure_openai.assert_called_once()

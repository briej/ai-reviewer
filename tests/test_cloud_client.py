import json
from unittest.mock import Mock, patch
from pathlib import Path

import pytest

from src.cloud_client import CloudClient, _ollama_request, _cloud_request, AIError


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_cloudclient_chat_openrouter_style():
    # Simulate OpenRouter-like response structure
    client = CloudClient("openrouter", api_key="KEY", model="m")

    payload = {"choices": [{"message": {"content": '{"issues": []}'}}]}

    with patch("src.cloud_client.requests.post", return_value=DummyResponse(payload)) as mock_post:
        out = client.chat("hello")
        assert '{"issues": []}' in out
        mock_post.assert_called_once()


def test_cloudclient_chat_ollama_style():
    # Simulate Ollama response (dict with 'response')
    client = CloudClient("ollama", api_key=None, model="m")

    payload = {"response": '{"issues": []}'}

    with patch("src.cloud_client.requests.post", return_value=DummyResponse(payload)) as mock_post:
        out = client.chat("hello")
        assert out == '{"issues": []}'
        mock_post.assert_called_once()


def test_cloud_request_missing_api_key_raises():
    # Provider requires API key (deepseek)
    with pytest.raises(AIError):
        _cloud_request("deepseek", "prompt", "m", api_key=None, timeout=1)

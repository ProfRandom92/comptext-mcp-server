"""
Tests for Ollama Cloud Client

Unit tests for the Ollama API client.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from comptext_mcp.mobile_agent.ollama_client import (
    OllamaCloudClient,
    ChatMessage,
    ChatResponse,
)
from comptext_mcp.mobile_agent.config import OllamaConfig, OllamaModel


class TestChatMessage:
    """Tests for ChatMessage dataclass."""

    def test_message_creation(self):
        """Test creating a chat message."""
        msg = ChatMessage(role="user", content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_to_dict(self):
        """Test converting to dictionary."""
        msg = ChatMessage(role="assistant", content="Hi there!")

        data = msg.to_dict()

        assert data["role"] == "assistant"
        assert data["content"] == "Hi there!"

    def test_message_with_tool_calls(self):
        """Test message with tool calls."""
        msg = ChatMessage(
            role="assistant",
            content="",
            tool_calls=[{"id": "call_1", "function": {"name": "test"}}],
        )

        data = msg.to_dict()
        assert "tool_calls" in data


class TestChatResponse:
    """Tests for ChatResponse dataclass."""

    def test_response_creation(self):
        """Test creating a chat response."""
        response = ChatResponse(
            message=ChatMessage(role="assistant", content="Response text"),
            model="qwen3-coder:480b",
            prompt_tokens=50,
            completion_tokens=30,
            total_tokens=80,
            finish_reason="stop",
        )

        assert response.message.content == "Response text"
        assert response.total_tokens == 80
        assert response.model == "qwen3-coder:480b"

    def test_response_finish_reason(self):
        """Test finish reason field."""
        response = ChatResponse(
            message=ChatMessage(role="assistant", content="Done"),
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            finish_reason="stop",
        )

        assert response.finish_reason == "stop"


class TestOllamaCloudClient:
    """Tests for OllamaCloudClient class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return OllamaConfig(
            api_base="https://api.test.com",
            api_key="test-api-key",
            model=OllamaModel.QWEN3_CODER,
            timeout=30,
            max_retries=2,
        )

    @pytest.fixture
    def client(self, config):
        """Create client instance."""
        return OllamaCloudClient(config)

    def test_client_creation(self, client, config):
        """Test client can be created."""
        assert client is not None
        assert client.config == config

    def test_client_has_metrics(self, client):
        """Test client has metrics tracking."""
        assert hasattr(client, "metrics")
        assert hasattr(client, "reset_metrics")

    @pytest.mark.asyncio
    async def test_context_manager(self, config):
        """Test async context manager."""
        async with OllamaCloudClient(config) as client:
            # Client should be initialized
            assert client._client is not None

    @pytest.mark.asyncio
    async def test_ensure_client(self, client):
        """Test client initialization."""
        await client._ensure_client()
        assert client._client is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_close_client(self, client):
        """Test client close."""
        await client._ensure_client()
        await client.close()
        assert client._client is None


class TestOllamaModels:
    """Tests for Ollama model configurations."""

    def test_model_enum_values(self):
        """Test model enum values."""
        assert OllamaModel.QWEN3_CODER.value == "qwen3-coder:480b"
        assert OllamaModel.DEEPSEEK_V3.value == "deepseek-v3.2:671b"
        assert OllamaModel.NEMOTRON_NANO.value == "nemotron-3-nano:30b"

    def test_model_selection(self):
        """Test model selection in config."""
        config = OllamaConfig()
        config.model = OllamaModel.DEEPSEEK_V3

        assert config.model == OllamaModel.DEEPSEEK_V3
        assert config.model.value == "deepseek-v3.2:671b"


class TestTokenTracking:
    """Tests for token tracking."""

    @pytest.fixture
    def client(self):
        """Create client instance."""
        config = OllamaConfig(api_key="test-key")
        return OllamaCloudClient(config)

    def test_response_token_calculation(self):
        """Test token calculation in response."""
        response = ChatResponse(
            message=ChatMessage(role="assistant", content="Hello"),
            model="test",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            finish_reason="stop",
        )

        assert response.total_tokens == response.prompt_tokens + response.completion_tokens

    def test_metrics_reset(self, client):
        """Test metrics can be reset."""
        client.reset_metrics()
        assert client.metrics.baseline_tokens == 0
        assert client.metrics.comptext_tokens == 0


class TestMessageFormatting:
    """Tests for message formatting."""

    def test_system_message(self):
        """Test system message formatting."""
        msg = ChatMessage(role="system", content="You are a helpful assistant")
        data = msg.to_dict()

        assert data["role"] == "system"

    def test_user_message(self):
        """Test user message formatting."""
        msg = ChatMessage(role="user", content="What's the weather?")
        data = msg.to_dict()

        assert data["role"] == "user"

    def test_assistant_message(self):
        """Test assistant message formatting."""
        msg = ChatMessage(role="assistant", content="I don't have that info")
        data = msg.to_dict()

        assert data["role"] == "assistant"

    def test_message_list(self):
        """Test converting message list."""
        messages = [
            ChatMessage(role="system", content="Be helpful"),
            ChatMessage(role="user", content="Hi"),
            ChatMessage(role="assistant", content="Hello!"),
            ChatMessage(role="user", content="Thanks"),
        ]

        data = [m.to_dict() for m in messages]

        assert len(data) == 4
        assert data[0]["role"] == "system"
        assert data[-1]["role"] == "user"


class TestTokenMetrics:
    """Tests for TokenMetrics class."""

    def test_calculate_reduction(self):
        """Test token reduction calculation."""
        from comptext_mcp.mobile_agent.ollama_client import TokenMetrics

        metrics = TokenMetrics()
        metrics.baseline_tokens = 500
        metrics.comptext_tokens = 100
        metrics.calculate_reduction()

        assert metrics.reduction_percent == 80.0

    def test_calculate_reduction_zero_baseline(self):
        """Test reduction with zero baseline."""
        from comptext_mcp.mobile_agent.ollama_client import TokenMetrics

        metrics = TokenMetrics()
        metrics.baseline_tokens = 0
        metrics.comptext_tokens = 100
        metrics.calculate_reduction()

        assert metrics.reduction_percent == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

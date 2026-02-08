"""
Ollama Cloud Client

Async client for Ollama Cloud API with retry logic and CompText optimization.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional

import httpx

from .config import OllamaConfig, OllamaModel

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Chat message structure."""

    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: Optional[list[dict]] = None
    tool_call_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API requests."""
        data = {"role": self.role, "content": self.content}
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        return data


@dataclass
class ChatResponse:
    """Chat completion response."""

    message: ChatMessage
    model: str
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str


@dataclass
class TokenMetrics:
    """Token usage metrics for CompText comparison."""

    baseline_tokens: int = 0
    comptext_tokens: int = 0
    reduction_percent: float = 0.0

    def calculate_reduction(self):
        """Calculate token reduction percentage."""
        if self.baseline_tokens > 0:
            self.reduction_percent = (self.baseline_tokens - self.comptext_tokens) / self.baseline_tokens * 100


class OllamaCloudClient:
    """
    Async client for Ollama Cloud API.

    Features:
    - Automatic retry with exponential backoff
    - Token usage tracking
    - CompText DSL integration
    - Tool/function calling support
    """

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._metrics = TokenMetrics()

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self._client is None:
            headers = {
                "Content-Type": "application/json",
            }
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.config.api_base,
                headers=headers,
                timeout=httpx.Timeout(self.config.timeout),
            )

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def chat(
        self,
        messages: list[ChatMessage],
        model: Optional[OllamaModel] = None,
        tools: Optional[list[dict]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> ChatResponse:
        """
        Send chat completion request.

        Args:
            messages: List of chat messages
            model: Model to use (defaults to config.model)
            tools: List of tool definitions for function calling
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            ChatResponse with completion and token usage
        """
        await self._ensure_client()

        payload = {
            "model": (
                (model or self.config.model).value
                if isinstance(model or self.config.model, OllamaModel)
                else (model or self.config.model)
            ),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": False,
        }

        if tools:
            payload["tools"] = tools

        response = await self._request_with_retry("POST", "/v1/chat/completions", json=payload)

        choice = response["choices"][0]
        usage = response.get("usage", {})

        return ChatResponse(
            message=ChatMessage(
                role=choice["message"]["role"],
                content=choice["message"].get("content", ""),
                tool_calls=choice["message"].get("tool_calls"),
            ),
            model=response["model"],
            total_tokens=usage.get("total_tokens", 0),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: Optional[OllamaModel] = None,
        temperature: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """
        Stream chat completion.

        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature

        Yields:
            Content chunks as they arrive
        """
        await self._ensure_client()

        payload = {
            "model": (
                (model or self.config.model).value
                if isinstance(model or self.config.model, OllamaModel)
                else (model or self.config.model)
            ),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature or self.config.temperature,
            "stream": True,
        }

        async with self._client.stream("POST", "/v1/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        if content := delta.get("content"):
                            yield content
                    except json.JSONDecodeError:
                        continue

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Make HTTP request with exponential backoff retry.

        Args:
            method: HTTP method
            path: API path
            **kwargs: Additional request arguments

        Returns:
            JSON response data

        Raises:
            httpx.HTTPError: After all retries exhausted
        """
        last_error = None
        delays = [1, 2, 4]  # Exponential backoff delays

        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                last_error = e
                if attempt < self.config.max_retries:
                    delay = delays[min(attempt, len(delays) - 1)]
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.config.max_retries + 1}), " f"retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Request failed after {self.config.max_retries + 1} attempts: {e}")

        raise last_error

    @property
    def metrics(self) -> TokenMetrics:
        """Get token usage metrics."""
        return self._metrics

    def reset_metrics(self):
        """Reset token usage metrics."""
        self._metrics = TokenMetrics()


# Convenience function for quick usage
async def create_ollama_client(
    api_key: Optional[str] = None,
    model: OllamaModel = OllamaModel.QWEN3_CODER,
) -> OllamaCloudClient:
    """
    Create and initialize an Ollama Cloud client.

    Args:
        api_key: Ollama API key (defaults to OLLAMA_API_KEY env var)
        model: Model to use

    Returns:
        Initialized OllamaCloudClient
    """
    config = OllamaConfig(model=model)
    if api_key:
        config.api_key = api_key

    client = OllamaCloudClient(config)
    await client._ensure_client()
    return client

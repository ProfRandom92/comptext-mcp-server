"""
Mobile Agent Configuration

Centralized configuration for the mobile agent system.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class OllamaModel(str, Enum):
    """Available Ollama Cloud models."""

    QWEN3_CODER = "qwen3-coder:480b"  # Primary: agentic tasks, tool-use
    DEEPSEEK_V3 = "deepseek-v3.2:671b"  # Backup: complex reasoning
    NEMOTRON_NANO = "nemotron-3-nano:30b"  # Local: fast UI parsing


class AgentMode(str, Enum):
    """Agent execution modes."""

    CLOUD = "cloud"  # Use Ollama Cloud
    LOCAL = "local"  # Use local Ollama instance
    HYBRID = "hybrid"  # Fast tasks local, complex tasks cloud


@dataclass
class OllamaConfig:
    """Ollama API configuration."""

    api_base: str = field(default_factory=lambda: os.getenv("OLLAMA_API_BASE", "https://api.ollama.ai"))
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("OLLAMA_API_KEY"))
    model: OllamaModel = OllamaModel.QWEN3_CODER
    local_model: OllamaModel = OllamaModel.NEMOTRON_NANO
    timeout: int = 120
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class ADBConfig:
    """Android Debug Bridge configuration."""

    adb_path: str = field(default_factory=lambda: os.getenv("ADB_PATH", "adb"))
    device_serial: Optional[str] = field(default_factory=lambda: os.getenv("ANDROID_SERIAL"))
    screenshot_dir: str = field(default_factory=lambda: os.getenv("SCREENSHOT_DIR", "/tmp/mobile_agent"))
    timeout: int = 30


@dataclass
class AgentConfig:
    """Agent behavior configuration."""

    max_steps: int = 10
    retry_attempts: int = 3
    step_delay: float = 0.5  # Delay between steps in seconds
    verify_actions: bool = True  # Verify UI state after each action
    context_memory_size: int = 5  # Number of screens to keep in memory
    enable_reflection: bool = True  # Plan-Execute-Verify loop
    use_comptext: bool = True  # Enable CompText DSL optimization


@dataclass
class MobileAgentConfig:
    """Complete mobile agent configuration."""

    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    adb: ADBConfig = field(default_factory=ADBConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    mode: AgentMode = AgentMode.CLOUD
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    @classmethod
    def from_env(cls) -> "MobileAgentConfig":
        """Create configuration from environment variables."""
        return cls(
            ollama=OllamaConfig(),
            adb=ADBConfig(),
            agent=AgentConfig(),
            mode=AgentMode(os.getenv("AGENT_MODE", "cloud")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []

        if self.mode in (AgentMode.CLOUD, AgentMode.HYBRID):
            if not self.ollama.api_key:
                errors.append("OLLAMA_API_KEY is required for cloud/hybrid mode")

        if self.agent.max_steps < 1:
            errors.append("max_steps must be at least 1")

        if self.agent.retry_attempts < 0:
            errors.append("retry_attempts cannot be negative")

        return errors

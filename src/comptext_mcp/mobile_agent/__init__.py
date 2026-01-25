"""
CompText Mobile Agent Module

Android automation via Natural Language powered by:
- Ollama Cloud (qwen3-coder:480b, deepseek-v3.2:671b)
- DroidRun framework
- CompText DSL (80-85% token reduction)
- MCP Protocol

Author: Alexander Kölnberger
Created: 2026-01-25
"""

from .agents.mobile_agent import MobileAgent
from .config import MobileAgentConfig
from .ollama_client import OllamaCloudClient
from .droidrun_wrapper import DroidRunWrapper

__all__ = [
    "MobileAgent",
    "MobileAgentConfig",
    "OllamaCloudClient",
    "DroidRunWrapper",
]

__version__ = "0.1.0"

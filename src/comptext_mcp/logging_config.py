"""Logging configuration for CompText MCP Server"""

import logging
import sys
from typing import Optional
import os


def setup_logging(
    level: Optional[str] = None, format_string: Optional[str] = None, log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        log_file: Optional file path to write logs to

    Returns:
        Configured logger instance
    """
    # Get log level from env or parameter
    log_level = level or os.getenv("LOG_LEVEL", "INFO")

    # Default format with timestamp, level, module, and message
    if not format_string:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - " "%(funcName)s:%(lineno)d - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()), format=format_string, handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(format_string))
        logging.getLogger().addHandler(file_handler)

    logger = logging.getLogger("comptext_mcp")
    logger.info(f"Logging configured with level: {log_level}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"comptext_mcp.{name}")

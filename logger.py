"""
Centralized logging configuration for Flow Forecaster application.

This module provides a consistent logging interface across the application,
replacing scattered print() statements with structured logging.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from typing import Optional


def setup_logger(
    name: str = "flow_forecaster",
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure and return a logger instance with consistent formatting.

    Args:
        name: Logger name (default: "flow_forecaster")
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If not provided, uses FLOW_FORECASTER_LOG_LEVEL env var or INFO
        log_file: Path to log file. If not provided, uses FLOW_FORECASTER_LOG_FILE
                 env var or logs to console only

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Determine log level
    if level is None:
        level = os.environ.get('FLOW_FORECASTER_LOG_LEVEL', 'INFO').upper()

    logger.setLevel(getattr(logging, level))

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file is None:
        log_file = os.environ.get('FLOW_FORECASTER_LOG_FILE')

    if log_file:
        try:
            # Create rotating file handler (10MB max, 5 backup files)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not create log file {log_file}: {e}")

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance. If the root logger hasn't been configured, set it up.

    Args:
        name: Logger name. If None, returns the root flow_forecaster logger.
              If provided, returns a child logger (e.g., "flow_forecaster.api")

    Returns:
        Logger instance
    """
    root_logger = logging.getLogger("flow_forecaster")

    # If root logger not configured, configure it
    if not root_logger.handlers:
        setup_logger()

    if name:
        return logging.getLogger(f"flow_forecaster.{name}")
    return root_logger


# Create default logger instance for convenience
logger = get_logger()

#!/usr/bin/env python3
"""
Common utilities shared across the application.
"""

import logging
from typing import Dict, List, Tuple


def set_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger with consistent formatting.

    Args:
        name: Name of the logger
        level: Logging level (default: INFO)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Configure basic logging
    logging.basicConfig(
        level=level,
        format="(%(asctime)s)<%(levelname)s>[%(name)s]: %(message)s",
        datefmt="%m/%d|%H:%M",
    )

    # Get and return logger
    return logging.getLogger(name)


def setup_browser() -> Dict[str, int]:
    """Returns viewport settings."""
    return {"width": 1000, "height": 800}

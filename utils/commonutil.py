#!/usr/bin/env python3
"""
Common utilities shared across the application.
"""

import logging


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

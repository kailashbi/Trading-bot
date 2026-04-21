"""
Logging configuration for the Trading Bot.
Sets up both file and console handlers with structured formatting.
"""

import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


def setup_logger(name: str = "trading_bot") -> logging.Logger:
    """
    Configure and return a logger with both file and console handlers.

    Args:
        name: Logger name (default: 'trading_bot')

    Returns:
        Configured logging.Logger instance
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # --- File Handler (DEBUG level, full detail) ---
    log_filename = os.path.join(LOG_DIR, f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # --- Console Handler (INFO level, clean output) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.debug(f"Logger initialized. Log file: {log_filename}")
    return logger

"""Structured logging configuration for the trading bot."""

import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "trading.log"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the root logger with file and console handlers."""
    LOG_DIR.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # Quiet on console; use print for UX

    root_logger = logging.getLogger("trading_bot")
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.propagate = False

    return root_logger


logger = setup_logging()

"""
Binance Futures Testnet client factory.
Handles authentication, base URL configuration,
and server time synchronization.
"""

from __future__ import annotations

import os
import time

from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

from logging_config import logger

FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class ClientError(RuntimeError):
    """Raised when the Binance client cannot be initialised."""


def _sync_time(client: Client) -> None:
    """
    Synchronise local timestamp with Binance server time
    to prevent timestamp drift errors (-1021).
    """
    try:
        server_time = client.futures_time()
        local_time = int(time.time() * 1000)
        client.timestamp_offset = server_time["serverTime"] - local_time
        logger.info("Timestamp synchronised with Binance server.")
    except Exception as exc:
        logger.error("Failed to sync timestamp: %s", exc)
        raise ClientError(f"Failed to sync timestamp: {exc}") from exc


def get_client() -> Client:
    """
    Build and return an authenticated Binance client
    pointed at the Futures Testnet.
    Reads API_KEY and API_SECRET from environment or .env.
    """
    load_dotenv()

    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        raise ClientError(
            "API_KEY and API_SECRET must be set in the environment or .env file."
        )

    try:
        client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True,
        )

        # Explicitly set Futures Testnet URL
        client.FUTURES_URL = FUTURES_TESTNET_BASE_URL + "/fapi"

        # Sync server time to prevent timestamp errors
        _sync_time(client)

        logger.info("Binance Futures Testnet client initialised successfully.")
        return client

    except BinanceAPIException as exc:
        logger.error("Binance API error during client initialisation: %s", exc)
        raise ClientError(f"Binance API error: {exc}") from exc

    except Exception as exc:
        logger.error("Unexpected error during client initialisation: %s", exc)
        raise ClientError(f"Unexpected client error: {exc}") from exc
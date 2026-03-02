"""Order placement logic for Binance Futures Testnet."""

from __future__ import annotations

from decimal import Decimal

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from requests.exceptions import ConnectionError, Timeout

from logging_config import logger
from validators import validate_order_params


class OrderError(RuntimeError):
    """Raised when an order cannot be placed."""


def _format_decimal(value: Decimal) -> str:
    """Format a Decimal for the Binance API (no trailing zeros, plain string)."""
    return format(value, "f")


def place_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
) -> dict:
    """
    Validate parameters and place a futures order on Binance Testnet.

    Returns the raw API response dict on success.
    Raises OrderError on any failure.
    """
    # Validate first — raises ValidationError on bad input
    params = validate_order_params(symbol, side, order_type, quantity, price)

    log_ctx = (
        f"symbol={params['symbol']} side={params['side']} "
        f"type={params['order_type']} qty={params['quantity']}"
    )
    if "price" in params:
        log_ctx += f" price={params['price']}"

    logger.info("Placing order: %s", log_ctx)

    try:
        api_kwargs: dict = {
            "symbol": params["symbol"],
            "side": params["side"],
            "type": params["order_type"],
            "quantity": _format_decimal(params["quantity"]),
        }

        if params["order_type"] == "LIMIT":
            api_kwargs["price"] = _format_decimal(params["price"])
            api_kwargs["timeInForce"] = "GTC"

        response = client.futures_create_order(**api_kwargs)
        logger.info(
            "Order placed successfully: orderId=%s status=%s",
            response.get("orderId"),
            response.get("status"),
        )
        return response

    except BinanceOrderException as exc:
        logger.error("Order rejected by exchange: %s", exc)
        raise OrderError(f"Order rejected: {exc.message}") from exc
    except BinanceAPIException as exc:
        logger.error("Binance API error: %s", exc)
        raise OrderError(f"Binance API error: {exc.message}") from exc
    except (ConnectionError, Timeout) as exc:
        logger.error("Network error while placing order: %s", exc)
        raise OrderError(f"Network error — check your connection: {exc}") from exc


def format_order_summary(params: dict) -> str:
    """Return a human-readable summary string for an order before placement."""
    lines = [
        "┌─── Order Summary ────────────────────────",
        f"│  Symbol     : {params['symbol']}",
        f"│  Side       : {params['side']}",
        f"│  Type       : {params['order_type']}",
        f"│  Quantity   : {params['quantity']}",
    ]
    if "price" in params:
        lines.append(f"│  Price      : {params['price']}")
    lines.append("└───────────────────────────────────────────")
    return "\n".join(lines)


def format_order_response(response: dict) -> str:
    """Return a human-readable summary string for a filled/acknowledged order."""
    lines = [
        "┌─── Order Response ───────────────────────",
        f"│  Order ID   : {response.get('orderId', 'N/A')}",
        f"│  Symbol     : {response.get('symbol', 'N/A')}",
        f"│  Side       : {response.get('side', 'N/A')}",
        f"│  Type       : {response.get('type', 'N/A')}",
        f"│  Status     : {response.get('status', 'N/A')}",
        f"│  Qty        : {response.get('origQty', 'N/A')}",
    ]
    avg_price = response.get("avgPrice") or response.get("price")
    if avg_price:
        lines.append(f"│  Avg Price  : {avg_price}")
    lines.append("└───────────────────────────────────────────")
    return "\n".join(lines)

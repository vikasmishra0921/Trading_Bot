"""Input validation for trading bot parameters."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


class ValidationError(ValueError):
    """Raised when user-provided trading parameters fail validation."""


def validate_symbol(symbol: str) -> str:
    """Return uppercased symbol or raise ValidationError."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValidationError("Symbol cannot be empty.")
    if not symbol.isalnum():
        raise ValidationError(
            f"Symbol '{symbol}' must contain only alphanumeric characters (e.g. BTCUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    """Return uppercased order side or raise ValidationError."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Return uppercased order type or raise ValidationError."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> Decimal:
    """Return Decimal quantity or raise ValidationError."""
    try:
        qty = Decimal(str(quantity)).normalize()
    except InvalidOperation:
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than zero, got {qty}.")
    return qty


def validate_price(price: str | float) -> Decimal:
    """Return Decimal price or raise ValidationError (only for LIMIT orders)."""
    try:
        p = Decimal(str(price)).normalize()
    except InvalidOperation:
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Price must be greater than zero, got {p}.")
    return p


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
) -> dict:
    """Validate all order parameters and return a clean params dict."""
    params = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
    }

    if params["order_type"] == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        params["price"] = validate_price(price)
    else:
        if price is not None:
            raise ValidationError("Price should not be provided for MARKET orders.")

    return params

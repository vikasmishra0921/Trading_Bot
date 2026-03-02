"""
CLI entry point for the Binance Futures Testnet trading bot.

Usage (non-interactive):
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
    python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3000

Usage (interactive — run with no arguments):
    python cli.py
"""

from __future__ import annotations

import argparse
import sys

from client import ClientError, get_client
from logging_config import logger
from orders import OrderError, format_order_response, format_order_summary, place_order
from validators import (
    ValidationError,
    validate_order_params,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _print_error(msg: str) -> None:
    print(f"\n  ✗  {msg}\n", file=sys.stderr)


def _prompt(label: str, *, hint: str = "") -> str:
    hint_str = f"  [{hint}]" if hint else ""
    return input(f"  {label}{hint_str}: ").strip()


def _prompt_validated(label: str, validator, *, hint: str = "") -> object:
    """Repeatedly prompt until the user enters a valid value."""
    while True:
        raw = _prompt(label, hint=hint)
        try:
            return validator(raw)
        except ValidationError as exc:
            _print_error(str(exc))


# ──────────────────────────────────────────────────────────────────────────────
# Interactive mode
# ──────────────────────────────────────────────────────────────────────────────

def interactive_mode() -> dict:
    """Guide the user through order entry and return a validated params dict."""
    print("\n╔══════════════════════════════════════════╗")
    print("║   Binance Futures Testnet — Trading Bot  ║")
    print("║           Interactive Mode               ║")
    print("╚══════════════════════════════════════════╝\n")

    symbol = _prompt_validated("Symbol", validate_symbol, hint="e.g. BTCUSDT")
    side = _prompt_validated("Side", validate_side, hint="BUY / SELL")
    order_type = _prompt_validated("Order type", validate_order_type, hint="MARKET / LIMIT")
    quantity = _prompt_validated("Quantity", validate_quantity, hint="e.g. 0.01")

    price = None
    if order_type == "LIMIT":
        price = _prompt_validated("Price", validate_price, hint="e.g. 42000.50")

    return validate_order_params(symbol, side, order_type, quantity, price)


def _confirm(params: dict) -> bool:
    """Show order summary and ask for confirmation. Returns True to proceed."""
    print()
    print(format_order_summary(params))
    answer = input("\n  Confirm order? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


# ──────────────────────────────────────────────────────────────────────────────
# CLI (argparse)
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Binance Futures Testnet trading bot — place MARKET or LIMIT orders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # Market buy
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

  # Limit sell
  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.5 --price 3200

  # Interactive mode (no arguments)
  python cli.py
        """,
    )
    parser.add_argument("--symbol", metavar="SYMBOL", help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", metavar="SIDE", help="BUY or SELL")
    parser.add_argument("--type", dest="order_type", metavar="TYPE", help="MARKET or LIMIT")
    parser.add_argument("--quantity", metavar="QTY", help="Order quantity")
    parser.add_argument("--price", metavar="PRICE", help="Limit price (LIMIT orders only)")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    return parser


def cli_mode(args: argparse.Namespace) -> dict:
    """Validate CLI arguments and return a clean params dict."""
    missing = [
        name
        for name, val in [
            ("--symbol", args.symbol),
            ("--side", args.side),
            ("--type", args.order_type),
            ("--quantity", args.quantity),
        ]
        if not val
    ]
    if missing:
        _print_error(f"Missing required arguments: {', '.join(missing)}")
        sys.exit(1)

    return validate_order_params(
        args.symbol,
        args.side,
        args.order_type,
        args.quantity,
        args.price,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    is_interactive = not any([args.symbol, args.side, args.order_type, args.quantity])

    try:
        if is_interactive:
            print("\nEntering interactive mode. Type Ctrl+C anytime to exit.\n")

            while True:
                try:
                    params = interactive_mode()

                    if not _confirm(params):
                        print("\n  Order cancelled.\n")
                        continue

                    print("\n  Placing order…")
                    client = get_client()
                    response = place_order(
                        client,
                        symbol=str(params["symbol"]),
                        side=str(params["side"]),
                        order_type=str(params["order_type"]),
                        quantity=params["quantity"],
                        price=params.get("price"),
                    )

                    print("\n  ✓  Order placed successfully!\n")
                    print(format_order_response(response))
                    print()

                    again = input("  Place another order? [Y/n]: ").strip().lower()
                    if again in {"n", "no"}:
                        print("\n  Goodbye.\n")
                        break

                except KeyboardInterrupt:
                    print("\n\n  Interrupted. Goodbye.\n")
                    break

        else:
            params = cli_mode(args)

            if not args.yes:
                if not _confirm(params):
                    print("\n  Order cancelled.\n")
                    sys.exit(0)

            print("\n  Placing order…")
            client = get_client()
            response = place_order(
                client,
                symbol=str(params["symbol"]),
                side=str(params["side"]),
                order_type=str(params["order_type"]),
                quantity=params["quantity"],
                price=params.get("price"),
            )

            print("\n  ✓  Order placed successfully!\n")
            print(format_order_response(response))
            print()

    except ValidationError as exc:
        _print_error(f"Validation error: {exc}")
        logger.warning("Validation error: %s", exc)
        sys.exit(1)
    except ClientError as exc:
        _print_error(f"Client error: {exc}")
        logger.error("Client error: %s", exc)
        sys.exit(1)
    except OrderError as exc:
        _print_error(f"Order error: {exc}")
        logger.error("Order error: %s", exc)
        sys.exit(1)

if __name__ == "__main__":
    main()

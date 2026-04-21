#!/usr/bin/env python3
"""
Usage examples:
  python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 50000
  python cli.py place --symbol ETHUSDT --side BUY --type STOP_MARKET --quantity 0.01 --price 2500
  python cli.py balance
  python cli.py orders --symbol BTCUSDT
"""

import argparse
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

from bot.client import BinanceClient, BinanceClientError, NetworkError
from bot.logging_config import setup_logger
from bot.orders import place_limit_order, place_market_order, place_stop_market_order
from bot.validators import validate_all, validate_quantity, validate_side, validate_symbol

#Load .env file if present
load_dotenv()

logger = setup_logger()

SEPARATOR = "─" * 60


# ─────────────────────────── helpers ────────────────────────────

def get_client() -> BinanceClient:
    """
    Build BinanceClient from environment variables.
    Exits with a clear message if credentials are missing.
    """
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print("\n   Missing API credentials!")
        print("   Set BINANCE_API_KEY and BINANCE_API_SECRET as environment variables,")
        print("   or place them in a .env file in the project root.\n")
        print("   Example .env:")
        print("     BINANCE_API_KEY=your_key_here")
        print("     BINANCE_API_SECRET=your_secret_here\n")
        logger.error("Missing BINANCE_API_KEY or BINANCE_API_SECRET environment variable.")
        sys.exit(1)

    return BinanceClient(api_key=api_key, api_secret=api_secret)


# ─────────────────────────── subcommands ────────────────────────

def cmd_place(args: argparse.Namespace):
    """Handle the 'place' subcommand."""
    logger.info(
        f"CLI place command received | symbol={args.symbol} side={args.side} "
        f"type={args.type} quantity={args.quantity} price={args.price}"
    )

    client = get_client()

    # Fetch current market price (for validation)
    try:
        ticker = client.client.futures_symbol_ticker(symbol=args.symbol.upper())
        current_price = float(ticker["price"])
        logger.info(f"Current market price: {current_price}")
    except Exception as e:
        logger.warning(f"Could not fetch market price: {e}")
        current_price = None

    # Validate all inputs (NOW WITH MARKET PRICE)
    try:
        params = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=str(args.quantity),
            price=str(args.price) if args.price is not None else None,
            current_price=current_price  
        )
    except ValueError as exc:
        print(f"\n  Validation error: {exc}\n")
        logger.error(f"Validation error: {exc}")
        sys.exit(1)

    order_type = params["order_type"]

    # Place order
    if order_type == "MARKET":
        place_market_order(
            client=client,
            symbol=params["symbol"],
            side=params["side"],
            quantity=params["quantity"],
        )

    elif order_type == "LIMIT":
        place_limit_order(
            client=client,
            symbol=params["symbol"],
            side=params["side"],
            quantity=params["quantity"],
            price=params["price"],
        )

    elif order_type == "STOP_MARKET":
        place_stop_market_order(
            client=client,
            symbol=params["symbol"],
            side=params["side"],
            quantity=params["quantity"],
            stop_price=params["price"],
        )


def cmd_balance(args: argparse.Namespace):
    """Handle the 'balance' subcommand."""
    client = get_client()
    logger.info("CLI balance command received.")

    try:
        balances = client.get_account_balance()
        print(f"\n{SEPARATOR}")
        print("  💰  ACCOUNT BALANCES (Futures Testnet)")
        print(SEPARATOR)
        found_any = False
        for asset in balances:
            wb = float(asset.get("withdrawAvailable", 0))
            balance = float(asset.get("balance", 0))
            if balance > 0 or wb > 0:
                found_any = True
                print(f"  {asset.get('asset'):10s}  Balance: {balance:>15.4f}  Available: {wb:>15.4f}")
        if not found_any:
            print("  No non-zero balances found.")
        print(SEPARATOR + "\n")

    except BinanceClientError as exc:
        print(f"\n  API error: {exc}\n")
        logger.error(f"Balance fetch failed: {exc}")
        sys.exit(1)
    except NetworkError as exc:
        print(f"\n  Network error: {exc}\n")
        logger.error(f"Balance fetch failed (network): {exc}")
        sys.exit(1)


def cmd_orders(args: argparse.Namespace):
    """Handle the 'orders' subcommand (list open orders)."""
    client = get_client()
    symbol = args.symbol.upper().strip() if args.symbol else None
    logger.info(f"CLI orders command received | symbol={symbol}")

    try:
        orders = client.get_open_orders(symbol=symbol)
        print(f"\n{SEPARATOR}")
        print(f"  📂  OPEN ORDERS{f' for {symbol}' if symbol else ''}")
        print(SEPARATOR)
        if not orders:
            print("  No open orders found.")
        for o in orders:
            print(
                f"  ID={o.get('orderId')}  {o.get('symbol')}  {o.get('side')}  "
                f"{o.get('type')}  qty={o.get('origQty')}  price={o.get('price')}  "
                f"status={o.get('status')}"
            )
        print(SEPARATOR + "\n")

    except BinanceClientError as exc:
        print(f"\n  API error: {exc}\n")
        logger.error(f"Open orders fetch failed: {exc}")
        sys.exit(1)
    except NetworkError as exc:
        print(f"\n  Network error: {exc}\n")
        logger.error(f"Open orders fetch failed (network): {exc}")
        sys.exit(1)


# ─────────────────────────── argument parser ────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Place a MARKET BUY order
  python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Place a LIMIT SELL order
  python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 50000

  # Place a STOP_MARKET BUY order (bonus order type)
  python cli.py place --symbol ETHUSDT --side BUY --type STOP_MARKET --quantity 0.01 --price 2500

  # Check account balance
  python cli.py balance

  # List open orders
  python cli.py orders --symbol BTCUSDT
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- place ---
    place_parser = subparsers.add_parser("place", help="Place a new order")
    place_parser.add_argument(
        "--symbol", required=True, metavar="SYMBOL",
        help="Trading pair symbol, e.g. BTCUSDT"
    )
    place_parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL"],
        help="Order side: BUY or SELL"
    )
    place_parser.add_argument(
        "--type", required=True, dest="type",
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type"
    )
    place_parser.add_argument(
        "--quantity", required=True, type=float, metavar="QTY",
        help="Order quantity (e.g. 0.001)"
    )
    place_parser.add_argument(
        "--price", required=False, type=float, default=None, metavar="PRICE",
        help="Limit / stop price (required for LIMIT and STOP_MARKET)"
    )
    place_parser.set_defaults(func=cmd_place)

    # --- balance ---
    balance_parser = subparsers.add_parser("balance", help="Show account balances")
    balance_parser.set_defaults(func=cmd_balance)

    # --- orders ---
    orders_parser = subparsers.add_parser("orders", help="List open orders")
    orders_parser.add_argument(
        "--symbol", required=False, default=None, metavar="SYMBOL",
        help="Filter by symbol (optional)"
    )
    orders_parser.set_defaults(func=cmd_orders)

    return parser


def main():
    print(f"\n{'═' * 60}")
    print("  Binance Futures Testnet Trading Bot")
    print(f"{'═' * 60}")

    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting.\n")
        logger.info("Bot interrupted by user (KeyboardInterrupt).")
        sys.exit(0)
    except Exception as exc:
        print(f"\n  Unexpected error: {exc}\n")
        logger.exception(f"Unexpected error in CLI: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Order placement logic and result formatting.
Wraps BinanceClient calls with rich logging and pretty output.
"""

from typing import Any, Dict, Optional

from .client import BinanceClient, BinanceClientError, NetworkError
from .logging_config import setup_logger

logger = setup_logger()

# Separator for CLI output readability
SEPARATOR = "─" * 60

def _print_order_request(symbol: str, side: str, order_type: str, quantity: float, price: Optional[float]):
    """Print a formatted order request summary to stdout."""
    print(f"\n{SEPARATOR}")
    print("  ORDER REQUEST SUMMARY")
    print(SEPARATOR)
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price is not None:
        print(f"  Price      : {price}")
    print(SEPARATOR)


def _print_order_response(response: Dict[str, Any]):
    """Print a formatted order response to stdout."""
    print(f"\n{SEPARATOR}")
    print("  ORDER RESPONSE")
    print(SEPARATOR)
    print(f"  Order ID   : {response.get('orderId', 'N/A')}")
    print(f"  Symbol     : {response.get('symbol', 'N/A')}")
    print(f"  Side       : {response.get('side', 'N/A')}")
    print(f"  Type       : {response.get('type', 'N/A')}")
    print(f"  Status     : {response.get('status', 'N/A')}")
    print(f"  Orig Qty   : {response.get('origQty', 'N/A')}")
    print(f"  Exec Qty   : {response.get('executedQty', 'N/A')}")
    avg_price = response.get('avgPrice') or response.get('price', 'N/A')
    print(f"  Avg Price  : {avg_price}")
    print(f"  Time       : {response.get('updateTime', 'N/A')}")
    print(SEPARATOR)
    print("  Order placed SUCCESSFULLY!\n")


def _print_error(message: str):
    """Print a formatted error message to stdout."""
    print(f"\n{SEPARATOR}")
    print("  ORDER FAILED")
    print(SEPARATOR)
    print(f"  Reason     : {message}")
    print(SEPARATOR + "\n")


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
) -> Optional[Dict[str, Any]]:
    """
    Place a MARKET order.

    Args:
        client:   BinanceClient instance
        symbol:   Trading pair
        side:     BUY or SELL
        quantity: Order quantity

    Returns:
        Order response dict on success, None on failure
    """
    logger.info(f"Placing MARKET order | {side} {quantity} {symbol}")
    _print_order_request(symbol, side, "MARKET", quantity, None)

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=quantity,
        )
        logger.info(
            f"MARKET order SUCCESS | orderId={response.get('orderId')} "
            f"status={response.get('status')} executedQty={response.get('executedQty')}"
        )
        _print_order_response(response)
        return response

    except BinanceClientError as exc:
        logger.error(f"MARKET order FAILED | Binance API error {exc.code}: {exc.message}")
        _print_error(str(exc))
        return None

    except NetworkError as exc:
        logger.error(f"MARKET order FAILED | Network error: {exc}")
        _print_error(f"Network error: {exc}")
        return None


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> Optional[Dict[str, Any]]:
    """
    Place a LIMIT order.

    Args:
        client:        BinanceClient instance
        symbol:        Trading pair
        side:          BUY or SELL
        quantity:      Order quantity
        price:         Limit price
        time_in_force: GTC | IOC | FOK

    Returns:
        Order response dict on success, None on failure
    """
    logger.info(f"Placing LIMIT order | {side} {quantity} {symbol} @ {price}")
    _print_order_request(symbol, side, "LIMIT", quantity, price)

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
        )
        logger.info(
            f"LIMIT order SUCCESS | orderId={response.get('orderId')} "
            f"status={response.get('status')} price={price}"
        )
        _print_order_response(response)
        return response

    except BinanceClientError as exc:
        logger.error(f"LIMIT order FAILED | Binance API error {exc.code}: {exc.message}")
        _print_error(str(exc))
        return None

    except NetworkError as exc:
        logger.error(f"LIMIT order FAILED | Network error: {exc}")
        _print_error(f"Network error: {exc}")
        return None


def place_stop_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
) -> Optional[Dict[str, Any]]:
    """
    Place a STOP_MARKET order (bonus order type).

    Args:
        client:     BinanceClient instance
        symbol:     Trading pair
        side:       BUY or SELL
        quantity:   Order quantity
        stop_price: Trigger price

    Returns:
        Order response dict on success, None on failure
    """
    logger.info(f"Placing STOP_MARKET order | {side} {quantity} {symbol} stopPrice={stop_price}")
    _print_order_request(symbol, side, "STOP_MARKET", quantity, stop_price)

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type="STOP_MARKET",
            quantity=quantity,
            stop_price=stop_price,
        )
        logger.info(
            f"STOP_MARKET order SUCCESS | orderId={response.get('orderId')} "
            f"status={response.get('status')} stopPrice={stop_price}"
        )
        _print_order_response(response)
        return response

    except BinanceClientError as exc:
        logger.error(f"STOP_MARKET order FAILED | Binance API error {exc.code}: {exc.message}")
        _print_error(str(exc))
        return None

    except NetworkError as exc:
        logger.error(f"STOP_MARKET order FAILED | Network error: {exc}")
        _print_error(f"Network error: {exc}")
        return None

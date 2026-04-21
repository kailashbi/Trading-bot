"""
Input validation logic for trading bot CLI parameters.
Raises ValueError with descriptive messages on invalid input.
"""

from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if not symbol.isalnum():
        raise ValueError(f"Invalid symbol '{symbol}'. Only alphanumeric characters allowed (e.g., BTCUSDT).")
    if len(symbol) < 3 or len(symbol) > 20:
        raise ValueError(f"Symbol '{symbol}' length must be between 3 and 20 characters.")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a numeric value (e.g., 0.01).")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0. Got: {qty}.")
    return qty


def validate_price(price: Optional[str], order_type: str) -> Optional[float]:
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid price '{price}'. Must be a numeric value (e.g., 50000.0).")
        if p <= 0:
            raise ValueError(f"Price must be greater than 0. Got: {p}.")
        return p

    if order_type == "STOP_MARKET":
        if price is None:
            raise ValueError("Stop price is required for STOP_MARKET orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid stop price '{price}'. Must be a numeric value.")
        if p <= 0:
            raise ValueError(f"Stop price must be greater than 0. Got: {p}.")
        return p

    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    current_price: Optional[float] = None,
) -> dict:
    """
    Run all validations and return a clean params dict.
    """

    # BASIC VALIDATION
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)

    # BUSINESS LOGIC 
    if order_type == "LIMIT" and current_price is not None:
        if side == "SELL" and price < current_price:
            raise ValueError(
                f"SELL price ({price}) must be >= current market price ({current_price})."
            )

        if side == "BUY" and price > current_price:
            raise ValueError(
                f"BUY price ({price}) must be <= current market price ({current_price})."
            )

    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
    }
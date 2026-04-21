"""
Binance Futures Testnet REST API client wrapper.
Handles authentication (HMAC-SHA256), request signing, and HTTP communication.
"""

import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from .logging_config import setup_logger

# Binance Futures Testnet base URL
BASE_URL = "https://testnet.binancefuture.com"

logger = setup_logger()


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error {code}: {message}")


class NetworkError(Exception):
    """Raised when a network/connection error occurs."""


class BinanceClient:
    """
    Thin wrapper around the Binance Futures Testnet REST API.

    Handles:
    - HMAC-SHA256 request signing
    - Timestamp synchronization
    - HTTP GET / POST with structured logging
    - Error parsing and propagation
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        """
        Initialize the client.

        Args:
            api_key:    Binance Futures Testnet API key
            api_secret: Binance Futures Testnet API secret
            base_url:   API base URL (defaults to testnet)
        """
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.debug(f"BinanceClient initialized. Base URL: {self.base_url}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_timestamp(self) -> int:
        """Return current UTC timestamp in milliseconds."""
        return int(time.time() * 1000)

    def _sign(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC-SHA256 signature for the given params dict.

        Args:
            params: Query/body parameters (must include timestamp)

        Returns:
            Hex-encoded signature string
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parse HTTP response and raise on error.

        Args:
            response: Raw requests.Response object

        Returns:
            Parsed JSON dict

        Raises:
            BinanceClientError: On non-2xx or API-level error
        """
        logger.debug(f"HTTP {response.status_code} from {response.url}")
        logger.debug(f"Response body: {response.text[:2000]}")  # truncate large payloads

        try:
            data = response.json()
        except ValueError:
            raise BinanceClientError(-1, f"Non-JSON response: {response.text[:500]}")

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            # Binance error payload: {"code": -XXXX, "msg": "..."}
            raise BinanceClientError(data.get("code", -1), data.get("msg", "Unknown error"))

        if not response.ok:
            raise BinanceClientError(response.status_code, response.text[:500])

        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> int:
        """
        Fetch server time (ms). Useful to diagnose timestamp skew.

        Returns:
            Server timestamp in milliseconds
        """
        url = f"{self.base_url}/fapi/v1/time"
        try:
            logger.debug(f"GET {url}")
            resp = self.session.get(url, timeout=10)
            data = self._handle_response(resp)
            return data["serverTime"]
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"Network error fetching server time: {exc}") from exc

    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch exchange info (trading rules, filters).

        Args:
            symbol: Optional symbol to filter

        Returns:
            Exchange info dict
        """
        url = f"{self.base_url}/fapi/v1/exchangeInfo"
        params = {}
        if symbol:
            params["symbol"] = symbol
        try:
            logger.debug(f"GET {url} params={params}")
            resp = self.session.get(url, params=params, timeout=10)
            return self._handle_response(resp)
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"Network error fetching exchange info: {exc}") from exc

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> Dict[str, Any]:
        """
        Place a futures order on Binance Testnet.

        Args:
            symbol:        Trading pair (e.g., BTCUSDT)
            side:          BUY or SELL
            order_type:    MARKET, LIMIT, or STOP_MARKET
            quantity:      Order quantity
            price:         Limit price (required for LIMIT orders)
            stop_price:    Stop trigger price (required for STOP_MARKET)
            time_in_force: GTC | IOC | FOK (for LIMIT orders)

        Returns:
            Order response dict from Binance

        Raises:
            BinanceClientError: On API error
            NetworkError:       On connectivity failure
        """
        url = f"{self.base_url}/fapi/v1/order"

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "timestamp": self._get_timestamp(),
            "recvWindow": 5000,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price must be provided for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        elif order_type == "STOP_MARKET":
            if stop_price is None:
                raise ValueError("Stop price must be provided for STOP_MARKET orders.")
            params["stopPrice"] = stop_price

        # Sign the payload
        params["signature"] = self._sign(params)

        logger.debug(f"POST {url} | Order params (pre-sign): symbol={symbol}, side={side}, "
                     f"type={order_type}, qty={quantity}, price={price}, stopPrice={stop_price}")

        try:
            resp = self.session.post(url, data=params, timeout=10)
            result = self._handle_response(resp)
            logger.debug(f"Order response: {result}")
            return result
        except requests.exceptions.ConnectionError as exc:
            raise NetworkError(f"Connection error: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            raise NetworkError(f"Request timed out: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"Unexpected network error: {exc}") from exc

    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        Fetch open orders, optionally filtered by symbol.

        Args:
            symbol: Optional trading pair filter

        Returns:
            List of open order dicts
        """
        url = f"{self.base_url}/fapi/v1/openOrders"
        params: Dict[str, Any] = {"timestamp": self._get_timestamp(), "recvWindow": 5000}
        if symbol:
            params["symbol"] = symbol
        params["signature"] = self._sign(params)

        logger.debug(f"GET {url} | symbol={symbol}")
        try:
            resp = self.session.get(url, params=params, timeout=10)
            return self._handle_response(resp)
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"Network error fetching open orders: {exc}") from exc

    def get_account_balance(self) -> list:
        """
        Fetch futures account balance.

        Returns:
            List of asset balance dicts
        """
        url = f"{self.base_url}/fapi/v2/balance"
        params: Dict[str, Any] = {"timestamp": self._get_timestamp(), "recvWindow": 5000}
        params["signature"] = self._sign(params)

        logger.debug(f"GET {url}")
        try:
            resp = self.session.get(url, params=params, timeout=10)
            return self._handle_response(resp)
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"Network error fetching account balance: {exc}") from exc

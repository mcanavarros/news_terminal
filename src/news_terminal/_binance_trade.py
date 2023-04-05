"""Module with class to handle trading in Binance"""
from decimal import Decimal

from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.helpers import round_step_size

from news_terminal.config import (
    BINANCE_KEY,
    BINANCE_KEY_TEST,
    BINANCE_SECRET,
    BINANCE_SECRET_TEST,
)


class BinanceTrader(object):
    """Class to handle trading in binance"""

    def __init__(self, testnet: bool) -> None:
        """Initialize shared attributes"""
        if testnet:
            self.client = Client(
                api_key=BINANCE_KEY_TEST,  # type: ignore
                api_secret=BINANCE_SECRET_TEST,  # type: ignore
                testnet=True,
            )
        else:
            self.client = Client(
                api_key=BINANCE_KEY,  # type: ignore
                api_secret=BINANCE_SECRET,  # type: ignore
                testnet=False,
            )

        self.symbols_precision = self.get_all_symbol_precision()

    def get_futures_balance(self, symbol: str = "USDT") -> Decimal:
        """Get the futures balance of the given symbol"""
        balance = self.client.futures_account_balance()
        token_balance = Decimal(0)
        for check_balance in balance:
            if check_balance["asset"] == symbol:
                token_balance = Decimal(check_balance["balance"])
        return token_balance

    def change_leverage(self, symbol: str, leverage: int) -> dict:
        try:
            return self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
        except BinanceAPIException:
            return {}

    def get_price(self, symbol: str) -> Decimal:
        """Get price of the given symbol."""
        token_price = self.client.futures_mark_price(symbol=symbol)
        token_price = Decimal(token_price["markPrice"])
        return token_price

    def get_all_symbol_precision(self) -> dict:
        info = self.client.futures_exchange_info()
        symbols_precision = {}
        for token in info["symbols"]:
            symbols_precision[token["symbol"]] = token["quantityPrecision"]
        return symbols_precision

    def calculate_position_side(
        self, symbol: str, money_to_spend: Decimal, leverage: int
    ) -> Decimal:
        token_price = self.get_price(symbol)
        return round(
            (money_to_spend * leverage) / token_price, self.symbols_precision[symbol]
        )

    def create_leverage_trade(
        self, symbol: str, side: str, order_type: str, quantity: Decimal, leverage: int
    ) -> dict:

        quantity = self.calculate_position_side(
            symbol=symbol, money_to_spend=quantity, leverage=leverage
        )
        trade = self.client.futures_create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
        )
        return trade

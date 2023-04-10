"""Module with a widget to watch prices"""
import asyncio
from textual import work

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Static
from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager

from news_terminal._binance_data import subscribe_to_market


class PriceTracker(Widget):
    """Widget to show price for tokens."""

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self._main_stream = None
        self._binance_api_manager: None | BinanceWebSocketApiManager = None
        self._current_market = None

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static("Current Price:", id="price_value"),
            id="price_layout",
        )
        yield Horizontal(
            Vertical(
                Static("Candle", classes="header"),
                Static("1m", classes="header"),
                Static("5m", classes="header"),
                Static("15m", classes="header"),
                id="header_col",
            ),
            Vertical(
                Static("Percent Change", classes="header"),
                Static("", id="m1_change", classes="up"),
                Static("", id="m5_change", classes="up"),
                Static("", id="m15_change", classes="up"),
            ),
            id="table_layout",
        )

    def on_mount(self) -> None:
        self.clear_values()
        self._update_values()

    def subscribe_to_action(self, market: str) -> None:
        if market.endswith("PERP"):
            market = market[:-5].lower()
            exchange = "binance.com-futures"
        else:
            market = market.replace("/", "").lower()
            exchange = "binance.com"

        if market == self._current_market:
            return

        self._current_market = market
        self.clear_values()

        self._binance_api_manager, self._main_stream = subscribe_to_market(
            self._binance_api_manager, self._main_stream, market, exchange
        )

    def clear_values(self) -> None:
        self.query_one("#price_value", Static).update("--")
        self.query_one("#m1_change", Static).update("--")
        self.query_one("#m5_change", Static).update("--")
        self.query_one("#m15_change", Static).update("--")

    @work(exclusive=True)
    async def _update_values(self):

        price_label = self.query_one("#price_value", Static)
        m1_change = self.query_one("#m1_change", Static)
        m5_change = self.query_one("#m5_change", Static)
        m15_change = self.query_one("#m15_change", Static)
        while True:
            await asyncio.sleep(0.1)
            if not self._binance_api_manager:
                continue

            if not self._binance_api_manager.get_active_stream_list():
                continue

            if self._binance_api_manager.is_manager_stopping():
                exit(0)

            oldest_data = self._binance_api_manager.pop_stream_data_from_stream_buffer(
                mode="LIFO"
            )
            if oldest_data:
                if not oldest_data.get("stream", "").startswith(self._current_market):
                    continue
                try:
                    oldest_data = oldest_data["data"]
                    if oldest_data["e"] == "trade":
                        price_label.update(f"Current price: ${oldest_data['p']}")
                    if oldest_data["e"] == "kline":
                        oldest_data = oldest_data["k"]
                        if oldest_data["i"] == "1m":
                            change = (
                                float(oldest_data["c"]) * 100 / float(oldest_data["o"])
                            ) - 100
                            m1_change.update(f"{change:.3f}%")
                            self._update_change_background(m1_change, change)
                        elif oldest_data["i"] == "5m":
                            change = (
                                float(oldest_data["c"]) * 100 / float(oldest_data["o"])
                            ) - 100
                            m5_change.update(f"{change:.3f}%")
                            self._update_change_background(m5_change, change)
                        elif oldest_data["i"] == "15m":
                            change = (
                                float(oldest_data["c"]) * 100 / float(oldest_data["o"])
                            ) - 100
                            m15_change.update(f"{change:.3f}%")
                            self._update_change_background(m15_change, change)
                except KeyError:
                    pass

    def _update_change_background(
        self, change_widget: Static, change_value: float
    ) -> None:
        if change_value > 0:
            if change_widget.has_class("down"):
                change_widget.remove_class("down")
                change_widget.add_class("up")
        else:
            if change_widget.has_class("up"):
                change_widget.remove_class("up")
                change_widget.add_class("down")

    def close_binance_manager(self):
        if self._binance_api_manager:
            self._binance_api_manager.stop_manager_with_all_streams()

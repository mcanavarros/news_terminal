"""Module with a widget to open positions on exchange."""
from datetime import datetime
from decimal import Decimal
import functools
from typing import Callable

from rich.console import RenderableType
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.screen import events
from textual.widget import Widget
from textual.widgets import Button, Input, Label, ListItem, ListView, Static, TextLog

from news_terminal._binance_trade import BinanceTrader
from news_terminal.widgets._label_item import LabelItem


class PositionManager(Widget):
    """Widget to open positions on exchange."""

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.binance_trader = BinanceTrader(testnet=True)
        self.current_pair = ""
        self.open_long = Button(
            "OPEN LONG", variant="success", disabled=True, id="open_long"
        )
        self.open_short = Button(
            "OPEN SHORT", variant="error", disabled=True, id="open_short"
        )
        self.confirm_dialog = ConfirmPositionDialog()

    def on_mount(self) -> None:
        self.update_exchange_holdings()

    def compose(self) -> ComposeResult:
        yield self.confirm_dialog
        yield Static("EXCHANGE DATA:", id="exchange_data")
        yield Horizontal(
            Static("Current USDT:", classes="title", id="usdt_label"),
            Static("$0", classes="value", id="current_usdt"),
        )
        yield Horizontal(
            Static("Bid:", classes="title", id="bid_label"),
            Input("1000", classes="value", id="bid_input"),
        )
        yield Horizontal(
            Static("Leverage:", classes="title", id="leverage_title"),
            RadioBox(
                LabelItem("2"),
                LabelItem("5"),
                LabelItem("7"),
                LabelItem("10"),
                LabelItem("20"),
                LabelItem("25"),
                LabelItem("50"),
                initial_index=3,
                id="leverage_selector",
            ),
        )
        yield Horizontal(
            self.open_short,
            self.open_long,
            id="position_buttons",
        )
        yield TextLog(id="binance_log", wrap=False, markup=True, highlight=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        current_leverage = self.query_one(RadioBox).highlighted_child.text  # type: ignore
        bid = self.query_one("#bid_input", Input).value
        if event.button.id == "open_long":
            long_partial = functools.partial(
                self.binance_trader.create_leverage_trade,
                self.current_pair.split(" ")[0].strip(),
                self.binance_trader.client.SIDE_BUY,
                self.binance_trader.client.FUTURE_ORDER_TYPE_MARKET,
                Decimal(bid),
                int(current_leverage),
            )
            self.confirm_dialog.confirm_text = "".join(
                f"Open LONG position {self.current_pair},"
                f" size: {bid}, leverage: {current_leverage}"
            )
            self.confirm_dialog.confirm_func = long_partial
        elif event.button.id == "open_short":
            short_partial = functools.partial(
                self.binance_trader.create_leverage_trade,
                self.current_pair.split(" ")[0].strip(),
                self.binance_trader.client.SIDE_SELL,
                self.binance_trader.client.FUTURE_ORDER_TYPE_MARKET,
                Decimal(bid),
                int(current_leverage),
            )
            self.confirm_dialog.confirm_text = "".join(
                f"Open SHORT position {self.current_pair},"
                f" size: {bid}, leverage: {current_leverage}"
            )
            self.confirm_dialog.confirm_func = short_partial
        self.confirm_dialog.show(True)

    def pair_selected(self, pair: str) -> None:
        self.open_long.disabled = False
        self.open_short.disabled = False
        self.current_pair = pair

    def increase_leverage(self) -> None:
        """Increase leverage index."""
        self.query_one(RadioBox).action_cursor_down()

    def reduce_leverage(self) -> None:
        """Reduce leverage index."""
        self.query_one(RadioBox).action_cursor_up()

    def update_exchange_holdings(self) -> None:
        """Update exchange holdings"""
        holdings = str(self.binance_trader.get_futures_balance("USDT"))
        self.query_one("#current_usdt", Static).update(holdings)

    def log_binance(self, renderable: RenderableType) -> None:
        self.query_one("#binance_log", TextLog).write(renderable)


class RadioBox(ListView):
    DEFAULT_CSS = """
    RadioBox {
        background: $boost;
        color: $text;
        padding: 0 2;
        border: tall $background;
        height: auto;
    }
    RadioBox > ListItem {
        padding: 1 1;
        width: 1fr;
        content-align: center middle;
    }
    """

    def __init__(
        self,
        *children: ListItem,
        initial_index: int | None = 0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            *children,
            initial_index=initial_index,
            name=name,
            id=id,
            classes=classes,
        )
        self.styles.layout = "horizontal"
        self.can_focus = False


class ConfirmPositionDialog(Widget):
    """Confirm Dialog for position."""

    confirm_text: reactive[str] = reactive("")

    def __init__(
        self,
        confirm_func: Callable | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.confirm_func = confirm_func
        self.can_focus = False
        self.border_title = "Confirm Position"

    def compose(self) -> ComposeResult:
        yield Label(self.confirm_text, id="confirm_label")
        yield Horizontal(
            Button("Confirm (Enter)", variant="success", id="confirm"),
            Button("Cancel (ESC)", variant="error", id="cancel"),
        )

    def watch_confirm_text(self, new_text) -> None:
        if new_text:
            self.query_one("#confirm_label", Label).update(new_text)

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self._confirm()
        if event.key == "escape":
            self.show(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self._confirm()
        elif event.button.id == "cancel":
            self.show(False)

    def _confirm(self) -> None:
        if self.confirm_func:
            print(datetime.now())
            value = self.confirm_func()
            buy_time = datetime.fromtimestamp(value["updateTime"] / 1000)
            value["buyTime"] = buy_time.strftime("%H:%M:%S:%f")
            self.app.log_binance(value)  # type: ignore
        self.show(False)

    def show(self, on: bool) -> None:
        if on:
            self.can_focus = True
            self.focus()
            self.add_class("-display-dialog")
        else:
            self.can_focus = False
            self.confirm_func = None
            self.app.set_focus(None)
            self.remove_class("-display-dialog")

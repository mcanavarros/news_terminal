"""Module with a widget to open positions on exchange."""
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Input, Label, ListItem, ListView, Static, Switch

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
        self.current_pair = ""
        self.open_long = Button(
            "OPEN LONG", variant="success", disabled=True, id="open_long"
        )
        self.open_short = Button(
            "OPEN SHORT", variant="error", disabled=True, id="open_short"
        )

    def compose(self) -> ComposeResult:
        yield Static("EXCHANGE DATA:", id="exchange_data")
        yield Horizontal(
            Static("Current USDT:", classes="title"),
            Static("$0", classes="value", id="current_usdt"),
            Static("Current BUSD:", classes="title"),
            Static("$0", classes="value", id="current_busd"),
        )
        yield Horizontal(
            Static("Bid:", classes="title", id="bit_label"),
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
            self.open_long,
            self.open_short,
            id="position_buttons",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open_long":
            self.app.push_screen(ConfirmPositionDialog())
            print(f"LONG {self.current_pair}")
        elif event.button.id == "open_short":
            print(f"SHORT {self.current_pair}")

    def pair_selected(self, pair: str) -> None:
        self.open_long.disabled = False
        self.open_short.disabled = False
        self.current_pair = pair


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
    BINDINGS = [
        Binding("left", "cursor_up", "Cursor Left", show=False),
        Binding("right", "cursor_down", "Cursor Right", show=False),
    ]

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


class ConfirmPositionDialog(Screen):
    """Confirm Dialog for position."""

    BINDINGS = [("escape,q", "pop_screen", "Close")]

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Button("Confirm (Enter)", variant="success"),
            Button("Cancel (ESC)", variant="error"),
        )

"""Module containg NewsTerminal main app."""
from subprocess import PIPE, Popen

from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Placeholder, TextLog

from news_terminal._binance_data import ACTIONS_DATA
from news_terminal.widgets._price_tracker import PriceTracker
from news_terminal.widgets._selection_display import SelectionDisplay
from news_terminal.widgets._position_manager import PositionManager
from news_terminal.widgets._news_container import (
    NewsContainer,
    NewsContent,
)
from news_terminal.widgets._config import ConfigPanel


class NewsTerminalApp(App):
    """News terminal user interface."""

    TITLE = "News Terminal"
    CSS_PATH = "terminal.css"
    BINDINGS = [
        ("f1", "app.toggle_class('TextLog', '-hidden')", "Logger"),
        ("f2", "app.toggle_class('ConfigPanel', '-hidden')", "Config"),
        ("f", "focus_search", "Focus Search"),
        ("w", "focus_long", "Focus Long"),
        ("s", "focus_short", "Focus Short"),
        ("n", "focus_news", "Focus Last News"),
    ]

    def add_note(self, renderable: RenderableType) -> None:
        self.query_one(TextLog).write(renderable)

    def compose(self) -> ComposeResult:
        logger = TextLog(classes="-hidden", wrap=False, highlight=True, markup=True)
        logger.can_focus = False
        yield ConfigPanel(classes="-hidden")
        yield Header(show_clock=True)
        yield Horizontal(
            Vertical(
                NewsContainer(),
                logger,
                id="news_feed",
            ),
            Vertical(
                SelectionDisplay(id="selection_display"),
                PriceTracker(id="price_tracker"),
                PositionManager(id="buy_action"),
            ),
        )
        yield Footer()

    def action_open_link(self, link: str):
        Popen(["wslview", link], stdout=PIPE, stderr=PIPE)

    def on_news_content_selected(self, message: NewsContent.Selected) -> None:
        actions = message.data["actions"]
        if not actions:
            coin = message.data["coin"].split(":")[-1].strip()
            actions = ACTIONS_DATA[coin]
        self.update_ticker(actions)

    def on_selection_display_button_selected(
        self, message: SelectionDisplay.ButtonSelected
    ) -> None:
        selection_display = self.query_one(SelectionDisplay)
        selection_display.selected_pair = message.pair
        self.subscribe_to_action(message.pair)

    def on_selection_display_search_complete(
        self, message: SelectionDisplay.SearchComplete
    ) -> None:
        self.update_ticker(message.actions)
        self.set_focus(None)

    def update_ticker(self, actions: list[dict]) -> None:
        if not actions:
            return
        selection_display = self.query_one(SelectionDisplay)
        selection_display.selected_pair = actions[0]["title"]
        selection_display.update_actions(actions)
        self.subscribe_to_action(actions[0]["title"])

    def subscribe_to_action(self, pair: str) -> None:
        self.query_one(PositionManager).pair_selected(pair)
        self.query_one(PriceTracker).subscribe_to_action(pair)

    def action_focus_news(self) -> None:
        self.set_focus(self.query(NewsContent).first())

    def action_focus_search(self):
        self.query_one(SelectionDisplay).query_one(Input).focus()

    def action_focus_long(self) -> None:
        self.query_one("PositionManager #open_long").focus()

    def action_focus_short(self) -> None:
        self.query_one("PositionManager #open_short").focus()

    async def action_quit(self) -> None:
        self.query_one(PriceTracker).close_binance_manager()
        return await super().action_quit()


if __name__ == "__main__":
    app = NewsTerminalApp()
    app.run()

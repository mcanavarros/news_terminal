"""Module containg NewsTerminal main app."""
from subprocess import PIPE, Popen

from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, TextLog

from news_terminal._binance_data import ACTIONS_DATA
from news_terminal.widgets._config import ConfigPanel
from news_terminal.widgets._news_container import NewsContainer, NewsContent
from news_terminal.widgets._position_manager import PositionManager
from news_terminal.widgets._price_tracker import PriceTracker
from news_terminal.widgets._selection_display import SelectionDisplay


class NewsTerminalApp(App):
    """News terminal user interface."""

    TITLE = "News Terminal"
    CSS_PATH = "terminal.css"
    BINDINGS = [
        ("f1", "app.toggle_class('#news_log', '-hidden')", "News Log"),
        ("f2", "app.toggle_class('ConfigPanel', '-hidden')", "Config"),
        ("a", "focus_news", "Focus Last News"),
        ("d", "focus_search", "Focus Search"),
        ("k", "focus_long", "Focus Long"),
        ("j", "focus_short", "Focus Short"),
        ("l", "increase_leverage", "Increase Leverage"),
        ("h", "reduce_leverage", "Reduce Leverage"),
    ]

    def on_mount(self) -> None:
        self.action_focus_news()

    def log_news(self, renderable: RenderableType) -> None:
        self.query_one("#news_log", TextLog).write(renderable)

    def compose(self) -> ComposeResult:
        logger = TextLog(
            classes="-hidden", wrap=False, highlight=True, markup=True, id="news_log"
        )
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

    def log_binance(self, renderable: RenderableType) -> None:
        self.query_one(PositionManager).log_binance(renderable)

    def action_focus_news(self) -> None:
        self.set_focus(self.query(NewsContent).first())

    def action_focus_search(self):
        self.query_one(SelectionDisplay).query_one(Input).focus()

    def action_focus_long(self) -> None:
        self.query_one("PositionManager #open_long").focus()

    def action_focus_short(self) -> None:
        self.query_one("PositionManager #open_short").focus()

    def action_increase_leverage(self) -> None:
        self.query_one(PositionManager).increase_leverage()

    def action_reduce_leverage(self) -> None:
        self.query_one(PositionManager).reduce_leverage()

    async def action_quit(self) -> None:
        price_tracker = self.query_one(PriceTracker)
        if price_tracker:
            price_tracker.close_binance_manager()
        return await super().action_quit()


if __name__ == "__main__":
    app = NewsTerminalApp()
    app.run()

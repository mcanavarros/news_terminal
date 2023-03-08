"""Module containg NewsTerminal main app."""
from subprocess import PIPE, Popen

from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Placeholder, TextLog

from news_terminal.widgets._price_tracker import PriceTracker
from news_terminal.widgets._selection_display import SelectionDisplay
from news_terminal.widgets._tree_news_container import (
    TreeNewsContainer,
    TreeNewsContent,
)


class NewsTerminalApp(App):
    """News terminal user interface."""

    TITLE = "News Terminal"
    CSS_PATH = "terminal.css"
    BINDINGS = [
        ("f1", "app.toggle_class('TextLog', '-hidden')", "Logger"),
        ("F", "focus_search", "Focus Search"),
    ]

    def add_note(self, renderable: RenderableType) -> None:
        self.query_one(TextLog).write(renderable)

    def compose(self) -> ComposeResult:
        logger = TextLog(classes="-hidden", wrap=False, highlight=True, markup=True)
        logger.can_focus = False
        yield Header(show_clock=True)
        yield Horizontal(
            Vertical(
                TreeNewsContainer(),
                logger,
                id="news_feed",
            ),
            Vertical(
                SelectionDisplay(id="selection_display"),
                PriceTracker(id="price_tracker"),
                Placeholder("buy_action zone", id="buy_action"),
            ),
        )
        yield Footer()

    def action_open_link(self, link: str):
        Popen(["wslview", link], stdout=PIPE, stderr=PIPE)

    async def on_tree_news_content_selected(
        self, message: TreeNewsContent.Selected
    ) -> None:
        await self.update_ticker(message.data["actions"])

    async def on_selection_display_button_selected(
        self, message: SelectionDisplay.ButtonSelected
    ) -> None:
        selection_display = self.query_one(SelectionDisplay)
        selection_display.selected_pair = message.pair
        await self.subscrite_to_action(message.pair)

    async def on_selection_display_search_complete(
        self, message: SelectionDisplay.SearchComplete
    ) -> None:
        await self.update_ticker(message.actions)

    async def update_ticker(self, actions: list[dict]) -> None:
        if not actions:
            return
        selection_display = self.query_one(SelectionDisplay)
        selection_display.selected_pair = actions[0]["title"]
        await selection_display.update_actions(actions)
        await self.subscrite_to_action(actions[0]["title"])

    async def subscrite_to_action(self, pair: str) -> None:
        await self.query_one(PriceTracker).subscrite_to_action(pair)

    async def action_focus_search(self):
        self.query_one(SelectionDisplay).query_one(Input).focus()

    async def action_quit(self) -> None:
        self.query_one(PriceTracker).close_binance_manager()
        return await super().action_quit()


if __name__ == "__main__":
    app = NewsTerminalApp()
    app.run()

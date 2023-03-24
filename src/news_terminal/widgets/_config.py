"""Module with config window"""
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import TabPane, TabbedContent

from news_terminal.widgets._twitter_config import TwitterConfig


class ConfigPanel(Container):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Twitter", id="twitter_tab"):
                yield TwitterConfig()

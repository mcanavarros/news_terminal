"""Module with config window"""
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Tab, Tabs

from news_terminal.widgets._twitter_config import TwitterConfig


class ConfigPanel(Container):
    def compose(self) -> ComposeResult:
        yield Tabs(Tab("Twitter", id="twitter_tab"))
        yield Vertical(
            TwitterConfig(),
        )

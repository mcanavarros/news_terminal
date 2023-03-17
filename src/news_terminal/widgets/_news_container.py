"""Module with Tree News widgets."""
import asyncio
from datetime import datetime

from textual.app import ComposeResult, events
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label

from news_terminal.news._twitter_monitor import subscribe_to_news_stream
from news_terminal.news._websocket import (
    format_news_data,
    format_news_message,
    subscribe_to_wss,
)
from news_terminal.news.data_format import NewsData


class NewsContainer(Container):
    """Container for News Content."""

    async def _add_new_entry(self) -> None:
        while True:
            json_msg = await self.news_queue.get()
            self.app.add_note(json_msg)  # type: ignore
            news_message = format_news_data(json_msg)
            new_news = NewsContent(news_message)
            self.mount(new_news, before=0)
            content_query = self.query(NewsContent)
            # Focus new content if a content is already in focus
            if isinstance(self.screen.focused, NewsContent):
                content_query.first().focus()

            if len(self.children) > 50:
                await content_query.last().remove()

    def on_mount(self):
        self.news_queue = asyncio.Queue()

        asyncio.create_task(
            subscribe_to_wss(self.news_queue, "news.treeofalpha.com/ws")
        )
        asyncio.create_task(subscribe_to_news_stream(self.news_queue))
        asyncio.create_task(self._add_new_entry())

    def compose(self) -> ComposeResult:
        yield NewsContent(
            format_news_data(
                {
                    "title": "BeaultifulTest fasdf asdfasdfasdf adf adf adsf asdf asd fa dfasdf asdf asdf adf asdf 1 ",
                    "url": "https://twitter.com/AnciliaInc/status/1634712824042905600",
                    "body": """Test""",
                    "source": "twitter",
                    "time": datetime.timestamp(datetime.now()) * 1000,
                    "coin": "BTC",
                    "_id": 1,
                    "actions": [
                        {
                            "action": "BINFUT_ATOMUSDT",
                            "title": "BTCUSDT PERP",
                            "icon": "https://news.treeofalpha.com/static/images/binance_icon.png",
                        },
                    ],
                }
            )
        )
        yield NewsContent(
            format_news_data(
                {
                    "title": "BeaultifulTest fasdf asdfasdfasdf adf adf adsf asdf asd fa dfasdf asdf asdf adf asdf 1 ",
                    "url": "https://twitter.com/AnciliaInc/status/1634712824042905600",
                    "body": """Test""",
                    "source": "twitter",
                    "time": datetime.timestamp(datetime.now()) * 1000,
                    "coin": "BTC",
                    "_id": 1,
                    "actions": [
                        {
                            "action": "BINFUT_ATOMUSDT",
                            "title": "BTCUSDT PERP",
                            "icon": "https://news.treeofalpha.com/static/images/binance_icon.png",
                        },
                    ],
                }
            )
        )
        yield NewsContent(
            format_news_data(
                {
                    "title": "BeaultifulTest fasdf asdfasdfasdf adf adf adsf asdf asd fa dfasdf asdf asdf adf asdf 1 ",
                    "url": "https://twitter.com/AnciliaInc/status/1634712824042905600",
                    "body": """Test""",
                    "source": "twitter",
                    "time": datetime.timestamp(datetime.now()) * 1000,
                    "coin": "BTC",
                    "_id": 1,
                    "actions": [
                        {
                            "action": "BINFUT_ATOMUSDT",
                            "title": "BTCUSDT PERP",
                            "icon": "https://news.treeofalpha.com/static/images/binance_icon.png",
                        },
                    ],
                }
            )
        )

    def clear_selection(self):
        self.query(NewsContent).remove_class("selected")


class NewsContent(Widget):
    """Widget to represent news content."""

    class Selected(Message):
        """Message sent when content selected"""

        def __init__(self, data: NewsData) -> None:
            self.data = data
            super().__init__()

    def __init__(self, data: NewsData) -> None:
        """Initialize shared variables."""
        self.data = data
        self.formated_data = format_news_message(data)
        self.can_focus = True
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose Widget"""
        yield Horizontal(
            Label(f"Source: {self.formated_data['source']}", id="source"),
            Vertical(
                Label(self.formated_data["title"], id="title", shrink=True),
                Label(self.formated_data["body"], id="body", shrink=True),
                Label(self.formated_data["link"], id="link"),
                Horizontal(
                    Label(
                        self.formated_data["time"].strftime("%H:%M:%S:%f"), id="time"
                    ),
                    Label(self.formated_data["coin"], id="coin"),
                ),
                Label(
                    f"Terminal delay: {(datetime.now() - self.formated_data['time']).total_seconds()*1000}ms",
                    id="delay",
                ),
            ),
        )

    async def on_click(self) -> None:
        """On click event."""
        self._select()

    async def on_key(self, event: events.Key) -> None:
        """On key event."""
        if event.key == "enter":
            self._select()
        elif event.key == "down":
            self.screen.focus_next()
        elif event.key == "up":
            self.screen.focus_previous()

    def _select(self) -> None:
        """Select content."""
        self.parent.clear_selection()  # type: ignore
        self.styles.animate(
            "opacity",
            value=0.1,
            duration=0.15,
            final_value=1.0,
        )
        self.add_class("selected")
        self.post_message(self.Selected(self.data))

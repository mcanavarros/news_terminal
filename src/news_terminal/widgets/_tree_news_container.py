"""Module with Tree News widgets."""
import asyncio
from datetime import datetime

from textual.app import ComposeResult, events
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message, MessageTarget
from textual.widget import Widget
from textual.widgets import Label

from news_terminal._news_websocket import (
    NewsData,
    format_news_data,
    format_news_message,
    subscribe_to_wss,
)


class TreeNewsContainer(Container):
    """Container for Tree News Content."""

    async def _add_new_entry(self) -> None:
        while True:
            json_msg = await self.news_queue.get()
            self.app.add_note(json_msg)  # type: ignore
            news_message = format_news_data(json_msg)
            new_news = TreeNewsContent(news_message)
            self.mount(new_news, before=0)
            content_query = self.query(TreeNewsContent)
            content_query.first().focus()

            if len(self.children) > 50:
                await content_query.last().remove()

    def on_mount(self):
        self.news_queue = asyncio.Queue()
        asyncio.create_task(
            subscribe_to_wss(self.news_queue, "news.treeofalpha.com/ws")
        )
        asyncio.create_task(self._add_new_entry())

    def compose(self) -> ComposeResult:
        yield TreeNewsContent(
            format_news_data(
                {
                    "title": "BeaultifulTest fasdf asdfasdfasdf adf adf adsf asdf asd fa dfasdf asdf asdf adf asdf 1 ",
                    "url": "https://news.treeofalpha.com",
                    "body": """wublockchain12: [https://finance.yahoo.com/news/republic-cancels-75-million-metaverse-060211106.html?guccounter=1&amp;guce_referrer=aHR0cHM6Ly9mb3Jlc2lnaHRuZXdzLnByby8&amp;guce_referrer_sig=AQAAAFODxVYXHGv1aW_0sLwInI1ODBuSX4tDTplvw9hZsG9lkZuAPw-B_lzrMK4uwEb2yzcn6ct1OG-D8uczUokonf5YccU40K-3u5NACTP4w41R7mwxp8Ic3lmkwTPOdzSOg9qCjywH4Kx3X1_lXRTjVWwRfGVLISPU2yca8iGKM17l] https://finance.yahoo.com/news/republic-cancels-75-million-metaverse-060211106.html?guccounter=1&guce_referrer=aHR0cHM6Ly9mb3Jlc2lnaHRuZXdzLnByby8&guce_referrer_sig=AQAAAFODxVYXHGv1aW_0sLwInI1ODBuSX4tDTplvw9hZsG9lkZuAPw-B_lzrMK4uwEb2yzcn6ct1OG-D8uczUokonf5YccU40K-3u5NACTP4w41R7mwxp8Ic3lmkwTPOdzSOg9qCjywH4Kx3X1_lXRTjVWwRfGVLISPU2yca8iGKM17l""",
                    "source": "twitter",
                    "time": datetime.timestamp(datetime.now()) * 1000,
                    "coin": "ETH",
                    "_id": 1,
                    "actions": [
                        {
                            "action": "BINFUT_ATOMUSDT",
                            "title": "ETHUSDT PERP",
                            "icon": "https://news.treeofalpha.com/static/images/binance_icon.png",
                        },
                        {
                            "action": "BIN_ATOM_USDT",
                            "title": "ATOM/USDT",
                            "icon": "https://news.treeofalpha.com/static/images/binance_icon.png",
                        },
                        {
                            "action": "BIN_ATOM_BTC",
                            "title": "ATOM/BTC",
                            "icon": "https://news.treeofalpha.com/static/images/binance_icon.png",
                        },
                        {
                            "action": "BIN_ATOM_BUSD",
                            "title": "ATOM/BUSD",
                            "icon": "https://news.treeofalpha.com/static/images/binance_icon.png",
                        },
                        {
                            "action": "BIN_ATOM_BNB",
                            "title": "ATOM/BNB",
                            "icon": "https://news.treeofalpha.com/static/images/binance_icon.png",
                        },
                        {
                            "action": "BIN_ATOM_ETH",
                            "title": "ATOM/ETH",
                            "icon": "https://news.treeofalpha.com/static/images/binance_icon.png",
                        },
                    ],
                }
            )
        )
        yield TreeNewsContent(
            format_news_data(
                {
                    "title": "BeaultifulTest fasdf asdfasdfasdf adf adf adsf asdf asd fa dfasdf asdf asdf adf asdf 1 ",
                    "url": "https://news.treeofalpha.com",
                    "body": """wublockchain12: [https://finance.yahoo.com/news/republic-cancels-75-million-metaverse-060211106.html?guccounter=1&amp;guce_referrer=aHR0cHM6Ly9mb3Jlc2lnaHRuZXdzLnByby8&amp;guce_referrer_sig=AQAAAFODxVYXHGv1aW_0sLwInI1ODBuSX4tDTplvw9hZsG9lkZuAPw-B_lzrMK4uwEb2yzcn6ct1OG-D8uczUokonf5YccU40K-3u5NACTP4w41R7mwxp8Ic3lmkwTPOdzSOg9qCjywH4Kx3X1_lXRTjVWwRfGVLISPU2yca8iGKM17l] https://finance.yahoo.com/news/republic-cancels-75-million-metaverse-060211106.html?guccounter=1&guce_referrer=aHR0cHM6Ly9mb3Jlc2lnaHRuZXdzLnByby8&guce_referrer_sig=AQAAAFODxVYXHGv1aW_0sLwInI1ODBuSX4tDTplvw9hZsG9lkZuAPw-B_lzrMK4uwEb2yzcn6ct1OG-D8uczUokonf5YccU40K-3u5NACTP4w41R7mwxp8Ic3lmkwTPOdzSOg9qCjywH4Kx3X1_lXRTjVWwRfGVLISPU2yca8iGKM17l""",
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
        self.query(TreeNewsContent).remove_class("selected")


class TreeNewsContent(Widget):
    """Widget to represent tree news content."""

    class Selected(Message):
        """Message sent when content selected"""

        def __init__(self, sender: MessageTarget, data: NewsData) -> None:
            self.data = data
            super().__init__(sender)

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

    async def _on_key(self, event: events.Key) -> None:
        """On key event."""
        if event.key == "enter":
            self._select()

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
        self.post_message_no_wait(self.Selected(self, self.data))

import asyncio
from asyncio import Queue
from datetime import datetime
import json
import re

from websockets.client import connect
from websockets.exceptions import ConnectionClosedError, InvalidStatusCode

from news_terminal.news.data_format import NewsData


async def subscribe_to_wss(wss_queue: Queue, url: str) -> None:
    """Subscribe to the given url and add to queue"""
    socket_url = f"wss://{url}"

    async def on_message(message):
        json_msg = json.loads(message)
        await wss_queue.put(json_msg)

    async with connect(socket_url, ping_interval=8, ping_timeout=8) as websocket:
        print(f"Opened {socket_url}")
        while True:
            try:
                message = await websocket.recv()
                await on_message(message)
            except (
                asyncio.TimeoutError,
                ConnectionClosedError,
                InvalidStatusCode,
            ) as e:
                print(e)
                break
    await asyncio.sleep(5)
    print("Restarting connection")
    await subscribe_to_wss(wss_queue, url)


def _format_links_for_click(text):
    """Format links to be used on click actions."""
    _text = re.sub(r"(?:https?://|www\.)\S+(?<![\!)\]])", _replace_with_click, text)
    return _text


def _replace_with_click(match) -> str:
    """Replace the matched url with a click format."""
    url = match.group(0)
    # Remove enclosings
    url = re.sub(r"[{}|^[\]`]", "", url)
    print(url)
    # # Remove everything after '
    url = re.sub(r"'.*$", "", url)
    print(url)
    link = _nice_link_format(url)
    return f'[@click=app.open_link("{url}")]{link}[/]'


def _nice_link_format(url):
    """Format the link text to a better display"""
    domain_pattern = r"(?<=://)[\w\.]+(?=/|$)"
    domain_match = re.search(domain_pattern, url)
    link = "Link"
    if domain_match:
        link = f"{domain_match.group()}/..."
    return link


def _format_quotes(text):
    """Remove [] from quotes to avoid error."""
    _text = re.sub(
        r"\[@(\w+)\]",
        r"@\1",
        text,
    )
    return _text


def format_news_data(news_message: dict) -> NewsData:
    """Format data from Tree Of Alpha."""

    _title = news_message.get("en", news_message.get("title", ""))
    _link = news_message.get("url", news_message.get("link", ""))
    _body = news_message.get("body", "")
    _source = news_message.get("source", news_message.get("type", ""))
    _time = datetime.fromtimestamp(news_message["time"] / 1000)
    _coin = news_message.get("coin", "")
    _id = news_message["_id"]
    _actions = news_message.get("actions", [])

    if not _coin and _actions:
        _coin = _actions[-1]["title"].split("/")[0]

    if news_message.get("type", None) == "direct":
        _source = "tree-twitter"

    if _source.lower() == "blogs":
        title_split = _title.split(":")
        _title = title_split[0].strip()
        _body = "".join(title_split[1:]).strip()

    return NewsData(
        title=_title,
        link=_link,
        body=_body,
        source=_source,
        time=_time,
        coin=_coin,
        tree_id=_id,
        actions=_actions,
    )


def format_news_message(news_message: NewsData) -> NewsData:

    # Remove @[Quote] to avoid conflicts
    news_message["title"] = _format_quotes(news_message["title"])
    # Click action on links
    news_message["title"] = _format_links_for_click(news_message["title"])

    if news_message["body"]:
        # Remove @[Quote] to avoid conflicts
        news_message["body"] = _format_quotes(news_message["body"])
        # Click action on links
        news_message["body"] = _format_links_for_click(news_message["body"])

    if news_message["link"]:
        _link = news_message["link"]
        _link = f'[@click=app.open_link("{_link}")]{_nice_link_format(_link)}[/]'
        news_message["link"] = _link

    if news_message["coin"]:
        news_message["coin"] = f"Coin: {news_message['coin']}"

    return news_message

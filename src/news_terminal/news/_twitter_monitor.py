"""Module with class to monitor twitter."""
from asyncio import Queue

from tweepy import Tweet, StreamRule
from tweepy.asynchronous.client import AsyncClient
from tweepy.asynchronous.streaming import AsyncStreamingClient

from news_terminal.config import TWITTER_BEARER_TOKEN
from news_terminal.news.data_format import NewsData


class NewsStream(AsyncStreamingClient):
    def __init__(self, bearer_token, client: AsyncClient, tweet_queue: Queue, **kwargs):
        super().__init__(bearer_token, **kwargs)
        self.tweet_queue = tweet_queue
        self.client = client

    async def on_tweet(self, tweet: Tweet) -> None:
        data = {}
        _title = await self.client.get_user(id=tweet.author_id)
        data["title"] = _title.data.name  # type: ignore
        data["body"] = tweet.text
        data["link"] = f"https://twitter.com/twitter/statuses/{tweet.id}"
        data["source"] = "terminal-twitter"
        data["time"] = tweet.created_at.timestamp() * 1000
        data["_id"] = 0
        await self.tweet_queue.put(data)


async def subscribe_to_news_stream(news_queue: Queue):
    twitter_client = AsyncClient(bearer_token=TWITTER_BEARER_TOKEN)
    news_stream = NewsStream(TWITTER_BEARER_TOKEN, twitter_client, news_queue)
    news_stream.filter(tweet_fields=["author_id", "created_at"])


async def add_tweet_user(username) -> None:
    await AsyncStreamingClient(TWITTER_BEARER_TOKEN).add_rules(
        StreamRule(f"from:{username}")
    )


async def get_current_rules() -> dict:
    """Get current rules from twitter api.

    Returns:
        dict[str][float]: Dict with user name and rule id
    """
    rules = await AsyncStreamingClient(TWITTER_BEARER_TOKEN).get_rules()
    rule_dict = {}
    if not rules.data:  # type: ignore
        return {}
    for rule in rules.data:  # type: ignore
        rule_dict[rule.value.split(":")[-1]] = rule.id
    return rule_dict


async def remove_tweet_user(username) -> None:
    current_rules = await get_current_rules()
    await AsyncStreamingClient(TWITTER_BEARER_TOKEN).delete_rules(
        ids=current_rules[username]
    )

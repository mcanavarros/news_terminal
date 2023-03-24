"""Module with twitter config."""
from textual.app import ComposeResult, events
from textual.containers import Container
from textual.widgets import Input, ListView

from news_terminal.news import _twitter_monitor
from news_terminal.widgets._label_item import LabelItem


class TwitterConfig(Container):
    async def on_mount(self):
        await self.update_tracked_users()

    async def update_tracked_users(self) -> None:
        tracked_users = await _twitter_monitor.get_current_rules()
        user_list = self.query_one("#tracked_users", ListView)
        with self.app.batch_update():
            user_list.clear()
            for user in tracked_users:
                user_list.append(LabelItem(user))

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Track username...", id="track_user")
        yield ListView(id="tracked_users")

    async def on_key(self, event: events.Key) -> None:
        if event.key == "delete":
            list_view = self.query_one("#tracked_users", ListView)
            item: LabelItem = list_view.highlighted_child  # type: ignore
            await _twitter_monitor.remove_tweet_user(item.text)
            await self.update_tracked_users()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Track user on input submitted"""
        await _twitter_monitor.add_tweet_user(event.value)
        await self.update_tracked_users()
        event.input.value = ""

"""Module with a widget to show selected coin and actions."""
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.message import Message, MessageTarget
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Static
from textual_autocomplete import AutoComplete, Dropdown, DropdownItem

from news_terminal._binance_data import build_actions_data

SUPPORTED_ACTION_TITLES = ["PERP", "USDT", "BUSD"]


class SelectionDisplay(Widget):

    selected_pair: reactive[str] = reactive("")

    class ButtonSelected(Message):
        """Message sent when button is selected"""

        def __init__(self, sender: MessageTarget, pair: str) -> None:
            self.pair = pair
            super().__init__(sender)

    class SearchComplete(Message):
        """Message sent when search is complete"""

        def __init__(self, sender: MessageTarget, actions: list[dict]) -> None:
            self.actions = actions
            super().__init__(sender)

    def compose(self) -> ComposeResult:
        self.action_data = build_actions_data()
        dropdown_items = [
            DropdownItem(main=ticker) for ticker in self.action_data.keys()
        ]

        yield AutoComplete(
            Input(placeholder="Type to select ticker..."),
            Dropdown(items=dropdown_items),
        )
        yield Horizontal(id="button_actions")
        yield Static(f"NO PAIR SELECTED", id="pair_text")

    async def watch_selected_pair(self, new_pair: str) -> None:
        if new_pair:
            self.query_one("#pair_text", Static).update(new_pair)
            self.add_class("-valid-pair")

    async def update_actions(self, actions: list[dict]) -> None:
        try:
            await self.query("#button_actions > Button").remove()
        except NoMatches:
            pass

        if not actions:
            return

        for action in actions:
            action_label = action["title"]
            if not action_label[-4:] in SUPPORTED_ACTION_TITLES:
                continue
            action_button = Button(action_label)
            action_button.can_focus = False
            await self.query_one("#button_actions", Horizontal).mount(action_button)

    async def on_auto_complete_selected(self, message: AutoComplete.Selected) -> None:
        actions = self.action_data[str(message.item.main)]
        self.query_one(Input).value = ""
        await self.post_message(self.SearchComplete(self, actions))

    def on_button_pressed(self, pressed: Button.Pressed) -> None:
        self.post_message_no_wait(self.ButtonSelected(self, str(pressed.button.label)))
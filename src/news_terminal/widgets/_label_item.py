from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, ListItem


class LabelItem(ListItem):
    DEFAULT_CSS = """
    LabelItem Label{
        content-align: center middle;
    }
    """

    def __init__(
        self,
        text: str,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.text = text

    def compose(self) -> ComposeResult:
        yield Label(self.text)

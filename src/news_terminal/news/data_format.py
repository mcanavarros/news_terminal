"""Module with Data format"""
from datetime import datetime
from typing import TypedDict


class NewsData(TypedDict):
    title: str
    link: str
    body: str
    source: str
    time: datetime
    coin: str
    tree_id: int
    actions: list[dict]

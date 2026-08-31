# feeds.py
from dataclasses import dataclass
from typing import Final
from research import NoArticle, Unavailable

@dataclass
class Wire:
    headline: str
    def latest(self) -> str:
        print("feed: fetching")
        return self.headline

class DeadWire:
    def latest(self) -> str:
        raise Unavailable("offline")

class DullWire:
    def latest(self) -> str:
        print("feed: fetching")
        return "local council approves new roundabout"

@dataclass
class Library:
    articles: dict[str, str]
    def article(self, topic: str) -> str:
        print(f"library: looking up {topic}")
        if topic not in self.articles:
            raise NoArticle(topic)
        return self.articles[topic]

STOCKS: Final[Wire] = Wire("stock market rising")
WEATHER: Final[Wire] = Wire("mild and cloudy")
SHELF: Final[Library] = Library(
    {"stock market": "a history"})
LONG: Final[Library] = Library({"genome": "chapter " * 40})

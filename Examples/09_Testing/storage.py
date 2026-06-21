# storage.py
import os
from pathlib import Path


def data_dir() -> Path:
    return Path(os.environ.get("APP_DATA", "."))


def save(name: str, value: str) -> None:
    (data_dir() / name).write_text(value, encoding="utf-8")


def load(name: str) -> str:
    return (data_dir() / name).read_text(encoding="utf-8")

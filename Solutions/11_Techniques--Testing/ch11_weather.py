# ch11_weather.py
import io
from collections.abc import Callable
from urllib.request import urlopen

type Url = str

def current_temp(city: str) -> str:
    with urlopen(f"https://example.com/{city}") as response:
        return response.read().decode()

def current_temp_with(
    city: str,
    fetch: Callable[[Url], io.BufferedIOBase],
) -> str:
    with fetch(f"https://example.com/{city}") as response:
        return response.read().decode()

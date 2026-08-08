# kw_only_config.py
from dataclasses import KW_ONLY, dataclass

@dataclass
class Config:
    source: str
    # Everything after this must be passed by keyword:
    _: KW_ONLY
    verbose: bool = False
    retries: int = 3

print(Config("data.csv", retries=5))
#: Config(source='data.csv', verbose=False, retries=5)

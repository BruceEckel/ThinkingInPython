# third_party_stub.py
from typing import Final
from row_check import check

APP: Final[str] = '''
import requests
from typing import Annotated
from effect_names import Network
from effect_rows import performs

def fetch(url: str) -> Annotated[str, performs(Network)]:
    return requests.get(url).text
'''
STUB: Final[str] = '''
from typing import Annotated
from effect_names import Network
from effect_rows import performs

def get(
    url: str,
) -> Annotated[object, performs(Network)]: ...
'''
print(check({"app": APP}).findings)
#: [Undeclared(where='app.fetch', effect='Unknown')]
print(check({"app": APP, "requests": STUB}).findings)
#: []

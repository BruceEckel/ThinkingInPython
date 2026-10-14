# third_party_stub.py
from typing import Final
from row_check import check, lines

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
for line in lines(check({"app": APP})):
    print(line)
#: app.fetch ['Network']
#: ! app.fetch undeclared Unknown
for line in lines(check({"app": APP, "requests": STUB})):
    print(line)
#: app.fetch ['Network']
#: requests.get ['Network']

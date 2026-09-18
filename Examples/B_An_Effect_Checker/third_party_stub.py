# third_party_stub.py
from row_check import check

APP = '''
import requests
from typing import Annotated
from effect_names import Network
from effect_rows import performs

def fetch(url: str) -> Annotated[str, performs(Network)]:
    return requests.get(url).text
'''
STUB = '''
from typing import Annotated
from effect_names import Network
from effect_rows import performs

def get(
    url: str,
) -> Annotated[object, performs(Network)]: ...
'''

def problems(sources: dict[str, str]) -> list[str]:
    return [f.problem for f in check(sources).findings]

print(problems({"app": APP}))
#: ['undeclared Unknown']
print(problems({"app": APP, "requests": STUB}))
#: []

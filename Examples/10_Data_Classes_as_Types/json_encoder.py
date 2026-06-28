# json_encoder.py
import json
from dataclasses import asdict, is_dataclass
from typing import Any, override
from person import EmailAddress, FullName, Person

class DataClassEncoder(json.JSONEncoder):
    @override
    def default(self, o: Any) -> Any:
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        return super().default(o)

people = [
    Person(FullName("Ada Lovelace"),
            EmailAddress("ada@example.com")),
    Person(FullName("Alan Turing"),
            EmailAddress("alan@example.com")),
]
print(json.dumps(people, cls=DataClassEncoder, indent=2))
#: [
#:   {
#:     "name": {
#:       "text": "Ada Lovelace"
#:     },
#:     "email": {
#:       "text": "ada@example.com"
#:     }
#:   },
#:   {
#:     "name": {
#:       "text": "Alan Turing"
#:     },
#:     "email": {
#:       "text": "alan@example.com"
#:     }
#:   }
#: ]

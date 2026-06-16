# json_encoder.py
# A custom encoder serializes any data class it meets, even nested
# inside other structures, by converting each one to a dict.
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from person import EmailAddress, FullName, Person


class DataClassEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        return super().default(o)


if __name__ == "__main__":
    people = [
        Person(FullName("Bruce Eckel"),
               EmailAddress("bruce@example.com")),
        Person(FullName("Ada Lovelace"),
               EmailAddress("ada@example.com")),
    ]
    print(json.dumps(people, cls=DataClassEncoder, indent=2))

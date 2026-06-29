# json_round_trip.py
import json
from dataclasses import asdict
from person import EmailAddress, FullName, Person

def to_json(person: Person) -> str:
    return json.dumps(asdict(person), indent=2)

def from_json(text: str) -> Person:
    data = json.loads(text)
    return Person(
        FullName(data["name"]["text"]),
        EmailAddress(data["email"]["text"]),
    )

original = Person(FullName("Bruce Eckel"),
                    EmailAddress("bruce@example.com"))
text = to_json(original)
print(text)
#: {
#:   "name": {
#:     "text": "Bruce Eckel"
#:   },
#:   "email": {
#:     "text": "bruce@example.com"
#:   }
#: }
print(from_json(text) == original)  # Round-trip
#: True

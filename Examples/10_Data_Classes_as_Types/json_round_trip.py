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

if __name__ == "__main__":
    original = Person(FullName("Bruce Eckel"),
                      EmailAddress("bruce@example.com"))
    text = to_json(original)
    print(text)
    print(from_json(text) == original)  # True: it round-trips

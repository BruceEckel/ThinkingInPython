# demo_person.py
from person import EmailAddress, FullName, Person

person = Person(
    FullName("Bruce Eckel"),
    EmailAddress("bruce@example.com"),
)
print(person.name)
#: FullName(text='Bruce Eckel')
print(person.email)
#: EmailAddress(text='bruce@example.com')

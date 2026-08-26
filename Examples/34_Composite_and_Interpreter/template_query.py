# template_query.py
from string.templatelib import Interpolation, Template

def to_query(
    template: Template) -> tuple[str, list[object]]:
    sql: list[str] = []
    values: list[object] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            sql.append("?")
            values.append(piece.value)
        else:
            sql.append(piece)
    return "".join(sql), values

def to_shape(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            parts.append(f"<{piece.expression}>")
        else:
            parts.append(piece)
    return "".join(parts)

name = "Alice'; DROP TABLE users; --"
limit = 18
query = (t"SELECT name FROM users WHERE name={name} "
         + t"AND age>{limit}")
sql, values = to_query(query)
print(sql)
#: SELECT name FROM users WHERE name=? AND age>?
print(values)
#: ["Alice'; DROP TABLE users; --", 18]
print(to_shape(query))
#: SELECT name FROM users WHERE name=<name> AND age><limit>

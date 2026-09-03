# template_query.py
from string.templatelib import Interpolation, Template

def to_query(
    template: Template) -> tuple[str, list[object]]:
    sql: list[str] = []
    values: list[object] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            if isinstance(piece.value, Template):
                nested_sql, nested_values = (
                    to_query(piece.value))
                sql.append(nested_sql)
                values.extend(nested_values)
            else:
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

inner = t"a={limit}"
outer = t"SELECT * FROM t WHERE {inner}"
sql2, values2 = to_query(outer)
print(sql2)
#: SELECT * FROM t WHERE a=?
print(values2)
#: [18]

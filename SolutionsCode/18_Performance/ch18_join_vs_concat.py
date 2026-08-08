# ch18_join_vs_concat.py
import timeit

def build_join(parts: list[str]) -> str:
    return "".join(parts)

def build_concat(parts: list[str]) -> str:
    out = ""
    for p in parts:
        out += p
    return out

many = ["ab"] * 10_000
few = ["ab"] * 100
assert build_join(many) == build_concat(many)

j_many = timeit.timeit(lambda: build_join(many), number=200)
c_many = timeit.timeit(lambda: build_concat(many), number=200)
print(f"join wins at 10,000 parts: {j_many < c_many}")
#: join wins at 10,000 parts: True

j_few = timeit.timeit(lambda: build_join(few), number=200)
c_few = timeit.timeit(lambda: build_concat(few), number=200)
print(f"join still wins at 100 parts: {j_few < c_few}")
#: join still wins at 100 parts: True
print(f"both under 50 microseconds per call at 100 parts: "
      f"{max(j_few, c_few) / 200 < 50e-6}")
#: both under 50 microseconds per call at 100 parts: True

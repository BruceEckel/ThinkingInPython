# lazy_imports.py
lazy import json
lazy from pathlib import Path

# Once used, the names behave like eager imports:
print(json.dumps({"a": 1}))
#: {"a": 1}
print(Path("report/data.txt").suffix)
#: .txt

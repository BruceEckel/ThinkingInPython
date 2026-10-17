# build_order.py
from graphlib import CycleError, TopologicalSorter
from exceptions import expected

deps: dict[str, tuple[str, ...]] = {
    "app": ("ui", "db"),
    "ui": ("core",),
    "db": ("core",),
}
print(list(TopologicalSorter(deps).static_order()))
#: ['core', 'ui', 'db', 'app']
deps["core"] = ("app",)
with expected(CycleError):
    list(TopologicalSorter(deps).static_order())
#: [CycleError] ('nodes are in a cycle', ['app', 'core',
#: 'ui', 'app'])

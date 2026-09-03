# resource_warning.py
import gc
import tempfile
import warnings
from pathlib import Path

path = Path(tempfile.gettempdir()) / "leaky.txt"
path.write_text("data")

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    f = open(path)
    f.read(1)
    del f
    gc.collect()
    print(caught[0].category.__name__)
#: ResourceWarning
path.unlink()

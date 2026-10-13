# resource_warning.py
import gc
import os
import warnings

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    f = open(os.devnull)
    del f
    gc.collect()
    print(caught[0].category.__name__)
#: ResourceWarning

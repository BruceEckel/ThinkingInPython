# dict_views.py

ages = {"Alice": 30, "Bob": 25, "Carol": 41}
names = ages.keys()
ages["Dan"] = 19
print(names)  # The view sees the new key
#: dict_keys(['Alice', 'Bob', 'Carol', 'Dan'])
other = {"Bob": 0, "Eve": 0}
print(names & other.keys())  # Set algebra on a view
#: {'Bob'}

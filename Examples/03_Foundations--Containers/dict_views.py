# dict_views.py

ages = {"Alice": 30, "Bob": 25, "Carol": 41}
other = {"Bob": 0, "Dan": 0}
print(ages.keys() & other.keys())  # Set algebra on a view
#: {'Bob'}

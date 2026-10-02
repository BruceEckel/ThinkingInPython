# ch18_bisect_duplicates.py
import bisect

xs = [1, 3, 5, 5, 5, 7, 9]
left = bisect.bisect_left(xs, 5)
right = bisect.bisect(xs, 5)  # bisect() is bisect_right()
print(left, right)
#: 2 5
print(xs[left])  # The first 5
#: 5
print(xs[right])  # One past the last 5
#: 7
print(xs[left:right])  # Every 5, as a slice
#: [5, 5, 5]

bisect.insort(xs, 5)  # insort() is insort_right()
print(xs)
#: [1, 3, 5, 5, 5, 5, 7, 9]

# heap_queue.py
import heapq

nums = [5, 1, 8, 3, 2]
heapq.heapify(nums)  # Rearrange into a min-heap in place
print(nums)
#: [1, 2, 8, 3, 5]
print(nums[0])  # The smallest stays at the front
#: 1
heapq.heappush(nums, 7)
print(nums)
#: [1, 2, 7, 3, 5, 8]
print(heapq.heappop(nums))  # Remove and return the smallest
#: 1
print(nums)
#: [2, 3, 7, 8, 5]
values = [5, 1, 8, 3, 2]
print(heapq.nsmallest(3, values))
#: [1, 2, 3]
print(heapq.nlargest(2, values))
#: [8, 5]
print(values)  # Neither call reorders its argument
#: [5, 1, 8, 3, 2]

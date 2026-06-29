# heap_queue.py
import heapq

nums = [5, 1, 8, 3, 2]
heapq.heapify(nums)         # Rearrange into a heap in place
print(nums[0])              # The smallest stays at the front
#: 1
heapq.heappush(nums, 0)
print(heapq.heappop(nums))  # Remove and return the smallest
#: 0
print(heapq.nsmallest(3, [5, 1, 8, 3, 2]))
#: [1, 2, 3]
print(heapq.nlargest(2, [5, 1, 8, 3, 2]))
#: [8, 5]

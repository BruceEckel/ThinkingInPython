# max_heap_queue.py
import heapq

max_nums = [5, 1, 8, 3, 2]
# Rearrange into a max-heap in place
heapq.heapify_max(max_nums)
print(max_nums)
#: [8, 3, 5, 1, 2]
print(max_nums[0])  # The largest stays at the front
#: 8
heapq.heappush_max(max_nums, 9)
print(max_nums)
#: [9, 3, 8, 1, 2, 5]
# Remove and return the largest
print(heapq.heappop_max(max_nums))
#: 9
print(max_nums)  # Heap ordering is maintained
#: [8, 3, 5, 1, 2]

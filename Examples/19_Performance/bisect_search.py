# bisect_search.py
import bisect

scores = [60, 70, 75, 90]      # Must stay sorted
i = bisect.bisect(scores, 78)  # Where 78 goes
print(i)
#: 3
bisect.insort(scores, 78)      # Insert and keep it sorted
print(scores)
#: [60, 70, 75, 78, 90]

def grade(score):
    # Map a score to a letter through its cutoff boundaries:
    cutoffs = [60, 70, 80, 90]
    letters = "FDCBA"
    return letters[bisect.bisect(cutoffs, score)]

print([grade(s) for s in (55, 65, 85, 95)])
#: ['F', 'D', 'B', 'A']

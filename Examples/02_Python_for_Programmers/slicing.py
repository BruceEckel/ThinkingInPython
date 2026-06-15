# slicing.py

xs = [10, 20, 30, 40, 50]
print(xs[0], xs[-1])  # 10 50: first and last
print(xs[1:3])        # [20, 30]: the stop index is excluded
print(xs[:2])         # [10, 20]: from the start
print(xs[2:])         # [30, 40, 50]: to the end
print(xs[::2])        # [10, 30, 50]: every second item
print(xs[::-1])       # [50, 40, 30, 20, 10]: reversed
xs.append(60)
xs.insert(0, 5)
print(len(xs), 30 in xs)  # 7 True

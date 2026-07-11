# lazy_noisy.py
lazy import noisy

print("before first use")
#: before first use
noisy.announce()  # noisy's body runs here, on first access
#: noisy module loaded
#: noisy.announce() called
print("after first use")
#: after first use

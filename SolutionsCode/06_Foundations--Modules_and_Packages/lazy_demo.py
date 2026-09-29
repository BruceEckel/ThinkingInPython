# lazy_demo.py
lazy import noisy
lazy import noisy2

print("before any use")
#: before any use
noisy2.announce()
#: noisy2 module loaded
#: noisy2.announce() called
print("between")
#: between
noisy.announce()
#: noisy module loaded
#: noisy.announce() called
print("after both")
#: after both

# lazy_demo.py
lazy import noisy
lazy import noisy2

print("before any use")
noisy2.announce()
print("between")
noisy.announce()
print("after both")
#: before any use
#: noisy2 module loaded
#: noisy2.announce() called
#: between
#: noisy module loaded
#: noisy.announce() called
#: after both

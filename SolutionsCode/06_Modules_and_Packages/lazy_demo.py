# lazy_demo.py
lazy import noisy
lazy import noisy2

print("before any use")
noisy2.announce()
print("between")
noisy.announce()
print("after both")
#: before any use
#: noisy2 module body running
#: noisy2 announces!
#: between
#: noisy module body running
#: noisy announces!
#: after both

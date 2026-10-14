# package_only.py
import a_package
from exceptions import expect

#: initializing a_package
expect(AttributeError, lambda: a_package.module1)  # type: ignore
#: [AttributeError] module 'a_package' has no attribute
#: 'module1'

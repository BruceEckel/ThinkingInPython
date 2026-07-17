# name_mangling.py

class Vault:
    def __init__(self) -> None:
        self._balance = 0  # Single underscore: convention only
        self.__pin = "1234"  # Double underscore: gets mangled

v = Vault()
print(vars(v))
#: {'_balance': 0, '_Vault__pin': '1234'}
# ty: unresolved attribute "_Vault__pin":
print(v._Vault__pin)  # type: ignore
#: 1234

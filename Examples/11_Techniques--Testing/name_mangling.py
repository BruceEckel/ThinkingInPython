# name_mangling.py

class Vault:
    def __init__(self) -> None:
        # Single underscore: convention only
        self._balance = 0
        # Double underscore: gets mangled
        self.__pin = "1234"

v = Vault()
print(vars(v))
#: {'_balance': 0, '_Vault__pin': '1234'}
# ty: unresolved attribute "_Vault__pin":
print(v._Vault__pin)  # type: ignore
#: 1234

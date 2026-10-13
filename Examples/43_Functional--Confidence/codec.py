# codec.py
def encode(text: str) -> str:
    # Reversible, and not its own inverse:
    return text.encode().hex()

def decode(encoded: str) -> str:
    return bytes.fromhex(encoded).decode()

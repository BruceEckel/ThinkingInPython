# codec.py
def encode(text: str) -> str:
    return text.encode().hex()

def decode(encoded: str) -> str:
    return bytes.fromhex(encoded).decode()

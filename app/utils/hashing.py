import hashlib


def sha256_from_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_from_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

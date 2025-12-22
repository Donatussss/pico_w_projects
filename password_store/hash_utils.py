import hashlib
import ubinascii
from random_utils import *

def create_password(password: str, salt: bytes = None, rounds: int = 100_000):
    if salt is None:
        salt = random_bytes(16)

    h = hash_password(password, salt, rounds)
    return {'salt': salt, 'rounds': rounds, 'hash': h}


def hash_password(password: str, salt: bytes, rounds: int = 100_000) -> bytes:
    if isinstance(password, str):
        password = password.encode("utf-8")

    h = salt + password
    for _ in range(rounds):
        h = hashlib.sha256(h).digest()

    return h

def constant_time_compare(a: bytes, b: bytes) -> bool:
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0

def verify_password(password: str, salt: bytes, rounds: int, stored_hash: bytes) -> bool:
    test_hash = hash_password(password, salt, rounds)
    return constant_time_compare(test_hash, stored_hash)

def get_store_hash(input_json):
    return {
        'salt': ubinascii.hexlify(input_json['salt']).decode(),
        'rounds': input_json['rounds'],
        'hash': ubinascii.hexlify(input_json['hash']).decode()
    }

def load_stored_hash(input_json):
    return {
        'salt': ubinascii.unhexlify(input_json['salt']),
        'rounds': input_json['rounds'],
        'hash': ubinascii.unhexlify(input_json['hash'])
    }
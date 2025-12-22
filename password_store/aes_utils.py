from random_utils import *
from ucryptolib import aes
import ubinascii

def pad(data: bytes, block_size=16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len

def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]

def encrypt_password(key, password: str) -> dict:
    iv = random_bytes(16)
    cipher = aes(key, 2, iv)  # 2 = CBC

    plaintext = pad(password.encode("utf-8"))
    ciphertext = cipher.encrypt(plaintext)

    return {
        "iv": ubinascii.hexlify(iv).decode(),
        "cipher": ubinascii.hexlify(ciphertext).decode()
    }

def decrypt_password(key, stored: dict) -> str:
    iv = ubinascii.unhexlify(stored["iv"])
    ciphertext = ubinascii.unhexlify(stored["cipher"])

    cipher = aes(key, 2, iv)
    plaintext = cipher.decrypt(ciphertext)

    return unpad(plaintext).decode("utf-8")

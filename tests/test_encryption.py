from src.encryption import aes_encrypt, chacha20_encrypt
import os

def test_aes_encrypt():
    key, iv = os.urandom(32), os.urandom(16)
    data = b"HelloWorld123456"
    encrypted = aes_encrypt(data, key, iv)
    assert len(encrypted) > 0

def test_chacha20_encrypt():
    key, nonce = os.urandom(32), os.urandom(16)
    data = b"HelloWorld123456"
    encrypted = chacha20_encrypt(data, key, nonce)
    assert len(encrypted) == len(data)

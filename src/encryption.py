from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from config import BACKEND

def aes_encrypt(data_bytes, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=BACKEND)
    padder = padding.PKCS7(128).padder()
    encryptor = cipher.encryptor()
    padded_data = padder.update(data_bytes) + padder.finalize()
    return encryptor.update(padded_data) + encryptor.finalize()

def chacha20_encrypt(data_bytes, key, nonce):
    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None, backend=BACKEND)
    encryptor = cipher.encryptor()
    return encryptor.update(data_bytes)

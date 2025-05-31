import os
from cryptography.hazmat.backends import default_backend

# AES Setup
AES_KEY = os.urandom(32)
IV = os.urandom(16)
BACKEND = default_backend()

# ChaCha20 Setup
CHACHA_KEY = os.urandom(32)  # 256-bit key

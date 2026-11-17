"""Hybrid selective encryption: AES-256-CBC for the ROI, ChaCha20 for the rest.

Every call gets a fresh IV and nonce, the full ciphertext is kept, and
decrypt_volume(encrypt_volume(x)) returns x exactly.
"""
import json
import os
from dataclasses import dataclass

import numpy as np
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

AES_BLOCK_BITS = 128


# ---------- primitives ----------

def aes_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    """AES-CBC with PKCS7 padding. Returns the full (padded) ciphertext."""
    padder = padding.PKCS7(AES_BLOCK_BITS).padder()
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return enc.update(padder.update(data) + padder.finalize()) + enc.finalize()


def aes_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = dec.update(ciphertext) + dec.finalize()
    unpadder = padding.PKCS7(AES_BLOCK_BITS).unpadder()
    return unpadder.update(padded) + unpadder.finalize()


def chacha20_encrypt(data: bytes, key: bytes, nonce: bytes) -> bytes:
    """ChaCha20 stream cipher.

    `nonce` is 16 bytes as the `cryptography` library expects:
    a 32-bit block counter followed by the 96-bit nonce (RFC 7539 layout).
    """
    return Cipher(algorithms.ChaCha20(key, nonce), mode=None).encryptor().update(data)


chacha20_decrypt = chacha20_encrypt  # XOR keystream: same operation both ways


def new_iv() -> bytes:
    return os.urandom(16)


def new_nonce() -> bytes:
    # 4-byte zero counter + 12 random bytes (96-bit nonce)
    return b"\x00" * 4 + os.urandom(12)


# ---------- keys ----------

@dataclass
class Keys:
    aes_key: bytes
    chacha_key: bytes

    @classmethod
    def generate(cls) -> "Keys":
        return cls(os.urandom(32), os.urandom(32))

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump({"aes_key": self.aes_key.hex(), "chacha_key": self.chacha_key.hex()}, f)
        os.chmod(path, 0o600)

    @classmethod
    def load(cls, path: str) -> "Keys":
        with open(path) as f:
            d = json.load(f)
        return cls(bytes.fromhex(d["aes_key"]), bytes.fromhex(d["chacha_key"]))


# ---------- volumes ----------

@dataclass
class EncryptedVolume:
    roi_ct: bytes
    non_roi_ct: bytes
    iv: bytes
    nonce: bytes
    shape: tuple
    dtype: str

    def view(self, roi_mask: np.ndarray) -> np.ndarray:
        """uint8 picture of the ciphertext, for visualization and metrics only."""
        out = np.zeros(self.shape, dtype=np.uint8)
        n_roi, n_non = int(roi_mask.sum()), int((~roi_mask).sum())
        out[roi_mask] = np.frombuffer(self.roi_ct[:n_roi], dtype=np.uint8)
        out[~roi_mask] = np.frombuffer(self.non_roi_ct[:n_non], dtype=np.uint8)
        return out

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        np.savez(path,
                 roi_ct=np.frombuffer(self.roi_ct, np.uint8),
                 non_roi_ct=np.frombuffer(self.non_roi_ct, np.uint8),
                 iv=np.frombuffer(self.iv, np.uint8),
                 nonce=np.frombuffer(self.nonce, np.uint8),
                 shape=np.array(self.shape), dtype=np.array(self.dtype))

    @classmethod
    def load(cls, path: str) -> "EncryptedVolume":
        d = np.load(path)
        return cls(d["roi_ct"].tobytes(), d["non_roi_ct"].tobytes(), d["iv"].tobytes(),
                   d["nonce"].tobytes(), tuple(int(s) for s in d["shape"]), str(d["dtype"]))


def encrypt_volume(volume: np.ndarray, roi_mask: np.ndarray, keys: Keys) -> EncryptedVolume:
    """AES-CBC on ROI voxels, ChaCha20 on the rest. Works for any dtype."""
    volume = np.ascontiguousarray(volume)
    iv, nonce = new_iv(), new_nonce()
    roi_ct = aes_encrypt(volume[roi_mask].tobytes(), keys.aes_key, iv)
    non_roi_ct = chacha20_encrypt(volume[~roi_mask].tobytes(), keys.chacha_key, nonce)
    return EncryptedVolume(roi_ct, non_roi_ct, iv, nonce, volume.shape, volume.dtype.str)


def decrypt_volume(enc: EncryptedVolume, roi_mask: np.ndarray, keys: Keys) -> np.ndarray:
    dtype = np.dtype(enc.dtype)
    out = np.empty(enc.shape, dtype=dtype)
    out[roi_mask] = np.frombuffer(aes_decrypt(enc.roi_ct, keys.aes_key, enc.iv), dtype=dtype)
    out[~roi_mask] = np.frombuffer(chacha20_decrypt(enc.non_roi_ct, keys.chacha_key, enc.nonce), dtype=dtype)
    return out


def encrypt_full_aes(volume: np.ndarray, key: bytes):
    """Baseline: AES-CBC on the whole volume. Returns (ciphertext, iv)."""
    iv = new_iv()
    return aes_encrypt(np.ascontiguousarray(volume).tobytes(), key, iv), iv


def decrypt_full_aes(ciphertext: bytes, key: bytes, iv: bytes, shape, dtype) -> np.ndarray:
    return np.frombuffer(aes_decrypt(ciphertext, key, iv), dtype=np.dtype(dtype)).reshape(shape)


def ciphertext_view(ciphertext: bytes, shape) -> np.ndarray:
    """uint8 picture of a full-volume ciphertext (first N bytes), for metrics only."""
    n = int(np.prod(shape))
    return np.frombuffer(ciphertext[:n], dtype=np.uint8).reshape(shape)

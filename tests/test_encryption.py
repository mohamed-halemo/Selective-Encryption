import numpy as np
import pytest

from encryption import (Keys, EncryptedVolume, aes_decrypt, aes_encrypt, chacha20_decrypt,
                        chacha20_encrypt, decrypt_full_aes, decrypt_volume, encrypt_full_aes,
                        encrypt_volume, new_iv, new_nonce)

rng = np.random.default_rng(0)


def make_volume(dtype=np.uint8, shape=(37, 41, 9)):
    vol = rng.integers(0, 255 if dtype == np.uint8 else 4000, shape).astype(dtype)
    mask = np.zeros(shape, bool)
    mask[10:20, 12:25, 2:7] = True
    return vol, mask


def test_aes_round_trip_and_padding():
    key, iv = Keys.generate().aes_key, new_iv()
    data = b"odd length payload!"
    ct = aes_encrypt(data, key, iv)
    assert len(ct) % 16 == 0 and len(ct) > len(data)
    assert aes_decrypt(ct, key, iv) == data


def test_chacha20_round_trip():
    key, nonce = Keys.generate().chacha_key, new_nonce()
    data = b"HelloWorld123456" * 5
    ct = chacha20_encrypt(data, key, nonce)
    assert len(ct) == len(data) and ct != data
    assert chacha20_decrypt(ct, key, nonce) == data


@pytest.mark.parametrize("dtype", [np.uint8, np.int16, np.float32])
def test_selective_round_trip(dtype):
    vol, mask = make_volume(dtype)
    keys = Keys.generate()
    enc = encrypt_volume(vol, mask, keys)
    out = decrypt_volume(enc, mask, keys)
    assert out.dtype == vol.dtype
    assert np.array_equal(out, vol)


def test_full_aes_round_trip():
    vol, _ = make_volume(np.int16)
    key = Keys.generate().aes_key
    ct, iv = encrypt_full_aes(vol, key)
    assert np.array_equal(decrypt_full_aes(ct, key, iv, vol.shape, vol.dtype), vol)


def test_fresh_iv_and_nonce_every_call():
    vol, mask = make_volume()
    keys = Keys.generate()
    a, b = encrypt_volume(vol, mask, keys), encrypt_volume(vol, mask, keys)
    assert a.iv != b.iv and a.nonce != b.nonce
    assert a.roi_ct != b.roi_ct and a.non_roi_ct != b.non_roi_ct


def test_wrong_key_does_not_decrypt():
    vol, mask = make_volume()
    enc = encrypt_volume(vol, mask, Keys.generate())
    with pytest.raises(Exception):
        out = decrypt_volume(enc, mask, Keys.generate())
        assert not np.array_equal(out, vol)
        raise ValueError("decrypted with wrong key")


def test_save_load(tmp_path):
    vol, mask = make_volume(np.int16)
    keys = Keys.generate()
    keys.save(str(tmp_path / "keys.json"))
    enc = encrypt_volume(vol, mask, keys)
    enc.save(str(tmp_path / "v.npz"))
    back = decrypt_volume(EncryptedVolume.load(str(tmp_path / "v.npz")), mask,
                          Keys.load(str(tmp_path / "keys.json")))
    assert np.array_equal(back, vol)


def test_view_shape():
    vol, mask = make_volume()
    enc = encrypt_volume(vol, mask, Keys.generate())
    view = enc.view(mask)
    assert view.shape == vol.shape and view.dtype == np.uint8

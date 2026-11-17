import numpy as np

from metrics import adjacent_correlation, chi_square, image_entropy

rng = np.random.default_rng(1)


def test_entropy_bounds():
    assert image_entropy(np.zeros((32, 32), np.uint8)) == 0
    assert image_entropy(rng.integers(0, 256, (256, 256), dtype=np.uint8)) > 7.99


def test_chi_square_low_for_uniform():
    uniform = rng.integers(0, 256, (512, 512), dtype=np.uint8)
    structured = np.tile(np.arange(64, dtype=np.uint8), (512, 8))
    assert chi_square(uniform) < 400  # ~255 expected; 293 is only a 5% cutoff
    assert chi_square(structured) > chi_square(uniform)


def test_adjacent_correlation():
    smooth = np.tile(np.linspace(0, 255, 256).astype(np.uint8), (256, 1))
    noise = rng.integers(0, 256, (256, 256), dtype=np.uint8)
    assert adjacent_correlation(smooth, axis=1) > 0.99
    assert abs(adjacent_correlation(noise, axis=1)) < 0.02

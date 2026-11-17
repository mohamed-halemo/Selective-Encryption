import numpy as np
from scipy.stats import entropy as scipy_entropy, chisquare

def psnr(img1, img2):
    """
    Peak Signal-to-Noise Ratio (PSNR)
    
    Measures the quality of encryption by comparing original and encrypted images.
    Lower PSNR values indicate better encryption (more noise/randomness).
    
    Range: 0 to infinity
    - Higher values (>30 dB): Poor encryption, images are too similar
    - Lower values (<20 dB): Good encryption, significant difference
    - Very low values (<10 dB): Excellent encryption, maximum difference
    
    Formula: 20 * log10(MAX_PIXEL_VALUE / sqrt(MSE))
    """
    mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
    if mse == 0:
        return float('inf')
    PIXEL_MAX = 255.0
    return 20 * np.log10(PIXEL_MAX / np.sqrt(mse))

def image_entropy(img):
    """
    Image Entropy
    
    Measures the randomness/unpredictability of pixel values in the image.
    Higher entropy indicates better encryption as it shows more uniform distribution.
    
    Range: 0 to 8 bits (for 8-bit images)
    - 0 bits: Completely predictable (all pixels same value)
    - 8 bits: Completely random (uniform distribution)
    - Original images: Usually 4-6 bits (structured content)
    - Well-encrypted images: 7-8 bits (high randomness)
    
    Formula: -sum(p * log2(p)) where p is probability of each pixel value
    """
    hist = np.bincount(img.astype(np.uint8).ravel(), minlength=256) / img.size
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist))

def correlation_coefficient(img1, img2):
    """
    Correlation Coefficient (CORR)
    
    Measures the linear relationship between original and encrypted pixel values.
    Values closer to 0 indicate better encryption (no correlation).
    
    Range: -1 to 1
    - 1: Perfect positive correlation (identical images)
    - 0: No correlation (good encryption)
    - -1: Perfect negative correlation (inverted images)
    - Original vs Original: Should be 1.0
    - Original vs Encrypted: Should be close to 0 for good encryption
    
    Formula: cov(X,Y) / (std(X) * std(Y))
    """
    return np.corrcoef(img1.flatten(), img2.flatten())[0, 1]

def mae(img1, img2):
    """
    Mean Absolute Error (MAE)
    
    Measures the average absolute difference between original and encrypted pixels.
    Higher MAE indicates better encryption (larger differences).
    
    Range: 0 to 255 (for 8-bit images)
    - 0: No difference (identical images)
    - 255: Maximum difference (completely different)
    - Original vs Original: Should be 0
    - Good encryption: 100-150 (significant differences)
    - Excellent encryption: 150-200 (large differences)
    
    Formula: mean(|original - encrypted|)
    """
    return np.mean(np.abs(img1.astype(np.float64) - img2.astype(np.float64)))

def npcr(img1, img2):
    """
    Number of Pixels Change Rate (NPCR)
    
    Measures the percentage of pixels that changed between original and encrypted images.
    Higher NPCR indicates better encryption (more pixels changed).
    
    Range: 0% to 100%
    - 0%: No pixels changed (identical images)
    - 100%: All pixels changed (completely different)
    - Original vs Original: Should be 0%
    - Good encryption: >95% (most pixels changed)
    - Excellent encryption: >99% (almost all pixels changed)
    
    Formula: (number of different pixels / total pixels) * 100
    """
    assert img1.shape == img2.shape
    diff = img1 != img2
    return 100.0 * np.sum(diff) / diff.size

def uaci(img1, img2):
    """
    Unified Average Changing Intensity (UACI)
    
    Measures the average intensity change between original and encrypted images.
    Higher UACI indicates better encryption (larger intensity changes).
    
    Range: 0% to 100%
    - 0%: No intensity change (identical images)
    - 100%: Maximum intensity change
    - Original vs Original: Should be 0%
    - Good encryption: 25-40% (significant intensity changes)
    - Excellent encryption: 30-35% (optimal range)
    
    Formula: mean(|original - encrypted| / 255) * 100
    """
    assert img1.shape == img2.shape
    return 100.0 * np.mean(np.abs(img1.astype(np.float64) - img2.astype(np.float64)) / 255)

def chi_square(img):
    """
    Chi-Square Test for Uniformity

    Tests whether pixel values are uniformly distributed over 0..255.
    LOWER is better for encrypted images (closer to uniform).

    - Ideal ciphertext: about 255 (degrees of freedom); below 293.25 passes at the 5% level
    - Original images: very large values (structured, non-uniform)

    Formula: sum((observed - expected)^2 / expected)
    """
    hist = np.bincount(img.astype(np.uint8).ravel(), minlength=256)
    expected = np.full(256, img.size / 256)
    chi2, _ = chisquare(hist, expected)
    return chi2


def adjacent_correlation(img, axis=0):
    """
    Correlation between neighbouring pixels along one axis (horizontal/vertical).
    Close to 1 for natural images, close to 0 for good ciphertext.
    """
    a = np.moveaxis(img.astype(np.float64), axis, 0)
    return np.corrcoef(a[:-1].ravel(), a[1:].ravel())[0, 1]


def differential_npcr_uaci(encrypt_fn, img, rng=None):
    """
    Classic differential test: flip one pixel, encrypt both images with the
    same key, and compare the two CIPHERTEXTS (not original vs ciphertext).
    encrypt_fn(img) -> uint8 array of the same shape.
    Returns (NPCR %, UACI %).
    """
    rng = rng or np.random.default_rng(0)
    img2 = img.copy()
    idx = tuple(int(rng.integers(0, s)) for s in img.shape)
    img2[idx] = (int(img2[idx]) + 1) % 256
    c1, c2 = encrypt_fn(img), encrypt_fn(img2)
    return npcr(c1, c2), uaci(c1, c2)

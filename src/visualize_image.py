from encryption import chacha20_encrypt,aes_encrypt
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import os
def visualize_image(image_path,mask_path):
    image = nib.load(image_path).get_fdata()
    mask = nib.load(mask_path).get_fdata()

    img_min, img_max = image.min(), image.max()
    img_uint8 = ((image - img_min) / (img_max - img_min) * 255).astype(np.uint8)

    roi_mask = np.isin(mask, [1, 2, 3])
    non_roi_mask = ~roi_mask

    # Prepare keys and nonce
    aes_key = os.urandom(32)
    iv = os.urandom(16)
    chacha_key = os.urandom(32)
    nonce = os.urandom(16)

    # Extract pixels
    roi_pixels = img_uint8[roi_mask]
    non_roi_pixels = img_uint8[non_roi_mask]

    # Encrypt ROI pixels (AES)
    encrypted_roi_bytes = aes_encrypt(roi_pixels.tobytes(), aes_key, iv)
    encrypted_roi_pixels = np.frombuffer(encrypted_roi_bytes[:len(roi_pixels)], dtype=np.uint8)

    # Encrypt non-ROI pixels (ChaCha20)
    encrypted_non_roi_bytes = chacha20_encrypt(non_roi_pixels.tobytes(), chacha_key, nonce)
    encrypted_non_roi_pixels = np.frombuffer(encrypted_non_roi_bytes[:len(non_roi_pixels)], dtype=np.uint8)

    selective_img = img_uint8.copy()
    selective_img[roi_mask] = encrypted_roi_pixels
    selective_img[non_roi_mask] = encrypted_non_roi_pixels

    # ROI-only encrypted image for comparison
    roi_only_img = img_uint8.copy()
    roi_only_img[roi_mask] = encrypted_roi_pixels

    mid_slice = img_uint8.shape[2] // 2
    slice_idx = mid_slice

    original_slice = img_uint8[:, :, slice_idx]
    roi_only_slice = roi_only_img[:, :, slice_idx]
    selective_slice = selective_img[:, :, slice_idx]
    mask_slice = mask[:, :, slice_idx]

    # ROI Highlighted RGB
    roi_highlighted = np.stack([original_slice]*3, axis=-1)
    roi_highlighted[mask_slice == 1] = [255, 0, 0]
    roi_highlighted[mask_slice == 2] = [0, 255, 0]
    roi_highlighted[mask_slice == 3] = [0, 0, 255]

    fig, axes = plt.subplots(1, 5, figsize=(25, 5))

    axes[0].imshow(original_slice, cmap='gray')
    axes[0].set_title('Original')
    axes[0].axis('off')

    axes[1].imshow(roi_highlighted)
    axes[1].set_title('ROI Highlighted (RGB Overlay)')
    axes[1].axis('off')
    # Add legend for ROI colors
    legend_patches = [
        mpatches.Patch(color='red', label='Right Ventricle'),
        mpatches.Patch(color='green', label='Myocardium'),
        mpatches.Patch(color='blue', label='Left Ventricle')
    ]
    axes[1].legend(handles=legend_patches, loc='lower right', fontsize=8)

    axes[2].imshow(roi_only_slice, cmap='gray')
    axes[2].set_title('ROI Only Encrypted (AES)')
    axes[2].axis('off')

    axes[3].imshow(selective_slice, cmap='gray')
    axes[3].set_title('Selective (AES ROI + ChaCha20 Non-ROI)')
    axes[3].axis('off')

# ... [above code unchanged] ...

    # Full AES encrypt the entire image slice
    full_slice = original_slice.copy()
    full_slice_bytes = full_slice.tobytes()
    full_encrypted_bytes = aes_encrypt(full_slice_bytes, aes_key, iv)
    # Decrypt length matches padded length, slice to original length:
    full_encrypted_pixels = np.frombuffer(full_encrypted_bytes[:full_slice.size], dtype=np.uint8)
    full_encrypted_img = full_encrypted_pixels.reshape(full_slice.shape)

    fig, axes = plt.subplots(1, 5, figsize=(25, 5))

    axes[0].imshow(original_slice, cmap='gray')
    axes[0].set_title('Original')
    axes[0].axis('off')

    axes[1].imshow(roi_highlighted)
    axes[1].set_title('ROI Highlighted (RGB Overlay)')
    axes[1].axis('off')
    # Add legend for ROI colors
    legend_patches = [
        mpatches.Patch(color='red', label='Right Ventricle'),
        mpatches.Patch(color='green', label='Myocardium'),
        mpatches.Patch(color='blue', label='Left Ventricle')
    ]
    axes[1].legend(handles=legend_patches, loc='lower right', fontsize=8)

    axes[2].imshow(roi_only_slice, cmap='gray')
    axes[2].set_title('ROI Only Encrypted (AES)')
    axes[2].axis('off')

    axes[3].imshow(selective_slice, cmap='gray')
    axes[3].set_title('Selective (AES ROI + ChaCha20 Non-ROI)')
    axes[3].axis('off')

    axes[4].imshow(full_encrypted_img, cmap='gray')
    axes[4].set_title('Full Image Encrypted (AES)')
    axes[4].axis('off')
    return fig
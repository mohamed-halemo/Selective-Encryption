# src/processing.py

import os
import time
import numpy as np
import nibabel as nib

from utils import (
    normalize_to_uint8,
    log_trial_average_timing_results,
    save_encrypted_images,
)
from encryption import aes_encrypt, chacha20_encrypt
from config import AES_KEY, IV, CHACHA_KEY


def process_patient_folder(base_dir, output_dir=None):
    """
    Process all patient folders inside a dataset directory.
    Returns all selective and full encryption times.
    """
    all_selective_times = []
    all_full_times = []

    for patient_id in sorted(os.listdir(base_dir)):
        patient_path = os.path.join(base_dir, patient_id)
        if not os.path.isdir(patient_path):
            continue

        selective_times, full_times = process_single_patient(patient_path, patient_id, output_dir)
        all_selective_times.extend(selective_times)
        all_full_times.extend(full_times)

    return all_selective_times, all_full_times


def process_single_patient(patient_path, patient_id, output_dir=None):
    """
    Process a single patient folder and perform selective and full encryption.
    """
    selective_times, full_times = [], []

    frame_files = [f for f in os.listdir(patient_path)
                   if f.endswith('.nii.gz') and "4d" not in f and not f.endswith("_gt.nii.gz")]

    for frame_file in sorted(frame_files):
        frame_name = frame_file.replace(".nii.gz", "")
        mask_file = f"{frame_name}_gt.nii.gz"
        mask_path = os.path.join(patient_path, mask_file)
        image_path = os.path.join(patient_path, frame_file)

        if not os.path.exists(mask_path):
            print(f"  Mask not found for {frame_file}, skipping...")
            continue

        # Load image and mask
        image = nib.load(image_path).get_fdata()
        mask = nib.load(mask_path).get_fdata()
        img_uint8 = normalize_to_uint8(image)

        # Create ROI and non-ROI masks
        roi_mask = np.isin(mask, [1, 2, 3])
        non_roi_mask = ~roi_mask

        roi_pixels = img_uint8[roi_mask]
        non_roi_pixels = img_uint8[non_roi_mask]

        # --- Selective Encryption ---
        start_sel = time.time()

        encrypted_roi_bytes = aes_encrypt(roi_pixels.tobytes(), AES_KEY, IV)
        encrypted_roi_pixels = np.frombuffer(encrypted_roi_bytes[:len(roi_pixels)], dtype=np.uint8)

        nonce = os.urandom(16)
        encrypted_non_roi_bytes = chacha20_encrypt(non_roi_pixels.tobytes(), CHACHA_KEY, nonce)
        encrypted_non_roi_pixels = np.frombuffer(encrypted_non_roi_bytes, dtype=np.uint8)

        selective_time = time.time() - start_sel
        selective_times.append(selective_time)

        # --- Full AES Encryption ---
        start_full = time.time()
        flat_img = img_uint8.flatten()
        full_encrypted = aes_encrypt(flat_img.tobytes(), AES_KEY, IV)
        full_img = np.frombuffer(full_encrypted[:len(flat_img)], dtype=np.uint8).reshape(img_uint8.shape)
        full_time = time.time() - start_full
        full_times.append(full_time)

        # Save images if output directory is provided
        if output_dir:
            save_encrypted_images(
                patient_id, frame_name, img_uint8, roi_mask, non_roi_mask,
                encrypted_roi_pixels, encrypted_non_roi_pixels, full_img,
                image_path, output_dir
            )

    return selective_times, full_times

def log_avg(log_file, avg_selective, avg_full, num_processed):
    """
    Wrapper to log timing results and return the logged row.
    """
    return log_trial_average_timing_results(log_file, avg_selective, avg_full, num_processed)

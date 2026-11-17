import os
import time

import nibabel as nib
import numpy as np

from config import ROI_LABELS
from encryption import (Keys, aes_encrypt, chacha20_encrypt, ciphertext_view, decrypt_volume,
                        encrypt_full_aes, encrypt_volume, new_iv, new_nonce)
from utils import log_trial_average_timing_results, normalize_to_uint8, save_nifti_image_from_array


def load_frame(image_path, mask_path, keep_intensity=False):
    """Load a volume and its ROI mask.

    keep_intensity=False -> 8-bit normalized volume (as in the paper).
    keep_intensity=True  -> original stored values (lossless, exact decryption).
    """
    img = nib.load(image_path)
    volume = np.asanyarray(img.dataobj) if keep_intensity else normalize_to_uint8(img.get_fdata())
    roi_mask = np.isin(nib.load(mask_path).get_fdata(), ROI_LABELS)
    return np.ascontiguousarray(volume), roi_mask


def time_frame(volume, roi_mask, keys, repeats=5, warmup=2):
    """Time only the crypto calls (the ROI split is done once beforehand, as in the paper).

    Returns mean seconds for (selective, full AES) over `repeats` runs.
    """
    roi_bytes = volume[roi_mask].tobytes()
    non_roi_bytes = volume[~roi_mask].tobytes()
    full_bytes = volume.tobytes()

    def selective():
        iv, nonce = new_iv(), new_nonce()
        t = time.perf_counter()
        aes_encrypt(roi_bytes, keys.aes_key, iv)
        chacha20_encrypt(non_roi_bytes, keys.chacha_key, nonce)
        return time.perf_counter() - t

    def full():
        iv = new_iv()
        t = time.perf_counter()
        aes_encrypt(full_bytes, keys.aes_key, iv)
        return time.perf_counter() - t

    for _ in range(warmup):
        selective(), full()
    sel = [selective() for _ in range(repeats)]
    ful = [full() for _ in range(repeats)]
    return float(np.mean(sel)), float(np.mean(ful))


def list_frames(patient_path):
    return sorted(f for f in os.listdir(patient_path)
                  if f.endswith(".nii.gz") and "4d" not in f and not f.endswith("_gt.nii.gz"))


def process_single_patient(patient_path, patient_id, keys, output_dir=None,
                           repeats=5, keep_intensity=False, verify=True):
    selective_times, full_times = [], []

    for frame_file in list_frames(patient_path):
        frame_name = frame_file.replace(".nii.gz", "")
        image_path = os.path.join(patient_path, frame_file)
        mask_path = os.path.join(patient_path, f"{frame_name}_gt.nii.gz")
        if not os.path.exists(mask_path):
            print(f"  Mask not found for {frame_file}, skipping...")
            continue

        volume, roi_mask = load_frame(image_path, mask_path, keep_intensity)

        sel_t, full_t = time_frame(volume, roi_mask, keys, repeats=repeats)
        selective_times.append(sel_t)
        full_times.append(full_t)

        if verify or output_dir:
            enc = encrypt_volume(volume, roi_mask, keys)
            if verify:
                assert np.array_equal(decrypt_volume(enc, roi_mask, keys), volume), \
                    f"Round trip failed for {frame_name}"
            if output_dir:
                save_outputs(patient_id, frame_name, volume, roi_mask, enc, keys, image_path, output_dir)

    return selective_times, full_times


def save_outputs(patient_id, frame_name, volume, roi_mask, enc, keys, reference_path, output_dir):
    """Save the decryptable ciphertext (.npz) plus uint8 NIfTI views for inspection/metrics."""
    stem = f"{patient_id}_{frame_name}"
    enc.save(os.path.join(output_dir, "selective", f"{stem}_selective_enc.npz"))
    save_nifti_image_from_array(enc.view(roi_mask), reference_path,
                                os.path.join(output_dir, "selective", f"{stem}_selective_enc.nii.gz"))

    full_ct, _ = encrypt_full_aes(volume, keys.aes_key)
    save_nifti_image_from_array(ciphertext_view(full_ct, volume.shape), reference_path,
                                os.path.join(output_dir, "full", f"{stem}_full_enc.nii.gz"))


def get_patient_ids(base_dir):
    return [f for f in sorted(os.listdir(base_dir)) if os.path.isdir(os.path.join(base_dir, f))]


def process_patient_folder(base_dir, keys, output_dir=None, repeats=5, keep_intensity=False,
                           verify=True, limit=None):
    all_sel, all_full = [], []
    ids = get_patient_ids(base_dir)[:limit] if limit else get_patient_ids(base_dir)
    for pid in ids:
        print(f"Processing {pid}...")
        sel, full = process_single_patient(os.path.join(base_dir, pid), pid, keys, output_dir,
                                           repeats, keep_intensity, verify)
        all_sel.extend(sel)
        all_full.extend(full)
    return all_sel, all_full


def log_avg(log_file, avg_selective, avg_full, num_processed):
    return log_trial_average_timing_results(log_file, avg_selective, avg_full, num_processed)

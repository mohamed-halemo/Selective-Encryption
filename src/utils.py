import numpy as np
import csv
import os
import nibabel as nib

def normalize_to_uint8(image):
    img_min, img_max = image.min(), image.max()
    return ((image - img_min) / (img_max - img_min) * 255).astype(np.uint8)
def log_trial_average_timing_results(log_path, avg_selective_time, avg_full_time, num_processed):
    """
    Logs average encryption times for a trial and returns the logged row.
    """
    header = ['trial', 'avg_selective_time', 'avg_full_time', 'faster_method', 'percentage_difference', 'num_processed']
    file_exists = os.path.isfile(log_path)

    # Determine trial number
    trial_number = 1
    if file_exists:
        with open(log_path, 'r') as f:
            existing_rows = sum(1 for _ in f) - 1
            trial_number = existing_rows + 1

    # Calculate metrics
    if avg_selective_time < avg_full_time:
        faster_method = "Selective"
        percentage = ((avg_full_time - avg_selective_time) / avg_full_time) * 100
    else:
        faster_method = "Full"
        percentage = ((avg_selective_time - avg_full_time) / avg_selective_time) * 100

    log_row = [
        trial_number,
        round(avg_selective_time, 5),
        round(avg_full_time, 5),
        faster_method,
        f"{percentage:.2f}%",
        num_processed
    ]

    with open(log_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(log_row)

    return log_row



def save_nifti_image_from_array(data_uint8, reference_nii_path, save_path):
    """
    Save a uint8 NumPy array as a NIfTI image using the affine and header from a reference file.
    """
    ref_img = nib.load(reference_nii_path)
    new_img = nib.Nifti1Image(data_uint8, affine=ref_img.affine, header=ref_img.header)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    nib.save(new_img, save_path)

def save_encrypted_images(
    patient_id, frame_name, img_uint8, roi_mask, non_roi_mask,
    encrypted_roi_pixels, encrypted_non_roi_pixels, full_img,
    reference_nii_path, output_dir
):
    """
    Save both selective and full encrypted images to disk.
    """
    selective_img = np.copy(img_uint8)
    selective_img[roi_mask] = encrypted_roi_pixels
    selective_img[non_roi_mask] = encrypted_non_roi_pixels

    selective_dir = os.path.join(output_dir, "selective")
    full_dir = os.path.join(output_dir, "full")

    selective_path = os.path.join(selective_dir, f"{patient_id}_{frame_name}_selective_enc.nii.gz")
    full_path = os.path.join(full_dir, f"{patient_id}_{frame_name}_full_enc.nii.gz")

    save_nifti_image_from_array(selective_img, reference_nii_path, selective_path)
    save_nifti_image_from_array(full_img, reference_nii_path, full_path)


def get_patient_ids(base_dir):
    """Return list of patient folder names (directories) inside base_dir."""
    return [f for f in sorted(os.listdir(base_dir)) if os.path.isdir(os.path.join(base_dir, f))]

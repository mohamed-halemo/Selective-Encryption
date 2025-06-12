import os
import nibabel as nib

def count_patient_slices(patient_path):
    """
    Count the total number of slices across all frames for a single patient.
    
    Args:
        patient_path (str): Path to the patient's directory containing NIfTI files
        
    Returns:
        int: Total number of slices across all frames
    """
    total_slices = 0
    
    # Get all frame files (excluding 4D files and ground truth masks)
    frame_files = [f for f in os.listdir(patient_path)
                  if f.endswith('.nii.gz') and "4d" not in f and not f.endswith("_gt.nii.gz")]
    
    for frame_file in sorted(frame_files):
        image_path = os.path.join(patient_path, frame_file)
        
        # Load the NIfTI image
        image = nib.load(image_path)
        
        # Get the number of slices (assuming the last dimension is slices)
        num_slices = image.shape[-1]
        total_slices += num_slices
        
        print(f"Frame {frame_file}: {num_slices} slices")
    
    print(f"Total slices across all frames: {total_slices}")
    return total_slices

def count_all_patients_slices(base_dir):
    """
    Count total slices for all patients in the base directory.
    
    Args:
        base_dir (str): Base directory containing patient folders
        
    Returns:
        dict: Dictionary mapping patient IDs to their total slice counts
    """
    patient_counts = {}
    
    # Get all patient directories
    patient_dirs = [d for d in os.listdir(base_dir) 
                   if os.path.isdir(os.path.join(base_dir, d))]
    
    for patient_id in sorted(patient_dirs):
        patient_path = os.path.join(base_dir, patient_id)
        print(f"\nProcessing patient: {patient_id}")
        
        total_slices = count_patient_slices(patient_path)
        patient_counts[patient_id] = total_slices
    
    return patient_counts

if __name__ == "__main__":
    # Example usage
    base_directory = "Data/Original"  # Replace with your data directory
    counts = count_all_patients_slices(base_directory)
    
    # Print summary
    print("\nSummary of slice counts:")
    total_slices_all_patients = 0
    for patient_id, count in counts.items():
        print(f"Patient {patient_id}: {count} total slices")
        total_slices_all_patients += count
    
    print(f"\nTotal slices across all {len(counts)} patients: {total_slices_all_patients}") 
        

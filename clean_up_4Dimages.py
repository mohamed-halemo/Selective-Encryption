import os
import glob

# Base directory where patient folders are located
base_dir = "Data/Original"

# Loop through all patient subfolders
for patient_folder in os.listdir(base_dir):
    patient_path = os.path.join(base_dir, patient_folder)

    if os.path.isdir(patient_path):
        # Find all files that contain '4d' in their filename
        matching_files = glob.glob(os.path.join(patient_path, "*4d*.nii.gz"))
        
        for file_path in matching_files:
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

print("Cleanup complete.")

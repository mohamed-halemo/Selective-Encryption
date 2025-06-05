import os
from processing import process_patient_folder, log_avg

base_dir = "../Data/Original"
output_dir = None  # or set if you want to save encrypted images

print("Starting processing all patients...")
all_selective_times, all_full_times = process_patient_folder(base_dir, output_dir)

if all_selective_times and all_full_times:
    avg_selective = sum(all_selective_times) / len(all_selective_times)
    avg_full = sum(all_full_times) / len(all_full_times)

    print("\n=== Average Encryption Times ===")
    print(f"Selective AES+ChaCha20 Encryption: {avg_selective:.5f} s")
    print(f"Full AES Encryption:               {avg_full:.5f} s")

    percentage = abs(avg_full - avg_selective) / max(avg_full, avg_selective) * 100
    faster = "Selective" if avg_selective < avg_full else "Full"
    print(f"\n{faster} encryption is faster by {percentage:.2f}%")

    # Logging
    log_file = "../results/timing_reports/encryption_times.csv"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    log_avg(log_file, avg_selective, avg_full)
else:
    print("No encryption times were recorded. Check if dataset is empty or paths are correct.")

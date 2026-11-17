"""Run selective vs full AES encryption on ACDC and log the timings.

Run from src/:
    python main.py                      # paper setup (8-bit volumes)
    python main.py --keep-intensity     # lossless, original voxel values
    python main.py --out ../results/encrypted --save-keys
"""
import argparse
import os

from config import DATA_DIR, KEYS_PATH, TIMING_LOG
from encryption import Keys
from processing import log_avg, process_patient_folder


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default=DATA_DIR, help="folder with patientXXX/ subfolders")
    p.add_argument("--out", default=None, help="save encrypted volumes here")
    p.add_argument("--repeats", type=int, default=5, help="timed runs per volume")
    p.add_argument("--limit", type=int, default=None, help="only the first N patients")
    p.add_argument("--keep-intensity", action="store_true", help="encrypt original values, not 8-bit")
    p.add_argument("--no-verify", action="store_true", help="skip the decrypt round-trip check")
    p.add_argument("--keys", default=None, help="load keys from this JSON file")
    p.add_argument("--save-keys", action="store_true", help=f"write keys to {KEYS_PATH}")
    p.add_argument("--log", default=TIMING_LOG)
    a = p.parse_args()

    keys = Keys.load(a.keys) if a.keys else Keys.generate()
    if a.save_keys:
        keys.save(KEYS_PATH)
        print(f"Keys saved to {KEYS_PATH} (keep this file private)")

    sel, full = process_patient_folder(a.data, keys, a.out, a.repeats, a.keep_intensity,
                                       verify=not a.no_verify, limit=a.limit)
    if not sel:
        print("No volumes processed. Check --data.")
        return

    avg_sel, avg_full = sum(sel) / len(sel), sum(full) / len(full)
    gain = (avg_full - avg_sel) / avg_full * 100
    print("\n=== Average encryption time per volume ===")
    print(f"Selective (AES ROI + ChaCha20): {avg_sel * 1e3:.3f} ms")
    print(f"Full AES:                       {avg_full * 1e3:.3f} ms")
    print(f"Speed gain:                     {gain:.2f}%  ({len(sel)} volumes)")

    os.makedirs(os.path.dirname(a.log), exist_ok=True)
    log_avg(a.log, avg_sel, avg_full, len(sel))


if __name__ == "__main__":
    main()

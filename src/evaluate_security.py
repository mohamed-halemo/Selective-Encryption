import os
import csv
import numpy as np
import nibabel as nib
from metrics import psnr, image_entropy, correlation_coefficient, npcr, uaci, chi_square, mae

def get_original_path(patient_id, frame_name):
    return os.path.join('Data/Original', patient_id, f'{patient_id}_{frame_name}.nii.gz')

def get_mask_path(patient_id, frame_name):
    return os.path.join('Data/Original', patient_id, f'{patient_id}_{frame_name}_gt.nii.gz')

def get_selective_path(patient_id, frame_name):
    return os.path.join('results/encrypted/selective', f'{patient_id}_{patient_id}_{frame_name}_selective_enc.nii.gz')

def get_full_path(patient_id, frame_name):
    return os.path.join('results/encrypted/full', f'{patient_id}_{patient_id}_{frame_name}_full_enc.nii.gz')

def normalize_to_uint8(image):
    img_min, img_max = image.min(), image.max()
    return ((image - img_min) / (img_max - img_min) * 255).astype(np.uint8)

def calculate_averages(results):
    """Calculate averages for each encryption type"""
    types = ['original', 'selective', 'full']
    averages = {}
    
    for enc_type in types:
        type_results = [r for r in results if r['type'] == enc_type]
        if not type_results:
            continue
            
        avg_row = {
            'patient': 'AVERAGE',
            'frame': enc_type.upper(),
            'type': enc_type,
            'psnr': '-',
            'entropy': np.mean([r['entropy'] for r in type_results]),
            'corr': np.mean([r['corr'] for r in type_results]),
            'npcr': np.mean([r['npcr'] for r in type_results]),
            'uaci': np.mean([r['uaci'] for r in type_results]),
            'chi2': np.mean([r['chi2'] for r in type_results]),
            'mae': np.mean([r['mae'] for r in type_results]),
        }
        
        # Calculate PSNR average only for selective and full (skip '-' values)
        if enc_type != 'original':
            psnr_values = [r['psnr'] for r in type_results if r['psnr'] != '-']
            if psnr_values:
                avg_row['psnr'] = np.mean(psnr_values)
        
        averages[enc_type] = avg_row
    
    return averages

def evaluate_all():
    selective_dir = 'results/encrypted/selective'
    results = []
    for fname in os.listdir(selective_dir):
        if not fname.endswith('_selective_enc.nii.gz'):
            continue
        parts = fname.split('_')
        patient_id = parts[0]
        frame_name = parts[2]
        orig_path = get_original_path(patient_id, frame_name)
        sel_path = get_selective_path(patient_id, frame_name)
        full_path = get_full_path(patient_id, frame_name)
        if not (os.path.exists(orig_path) and os.path.exists(sel_path) and os.path.exists(full_path)):
            print(f"Skipping {fname} due to missing files.")
            continue
        orig_img = nib.load(orig_path).get_fdata()
        sel_img = nib.load(sel_path).get_fdata()
        full_img = nib.load(full_path).get_fdata()
        orig_uint8 = normalize_to_uint8(orig_img)
        sel_uint8 = normalize_to_uint8(sel_img)
        full_uint8 = normalize_to_uint8(full_img)
        # Metrics for original
        row_orig = {
            'patient': patient_id,
            'frame': frame_name,
            'type': 'original',
            'psnr': '-',  # Not defined for original vs itself
            'entropy': image_entropy(orig_uint8),
            'corr': correlation_coefficient(orig_uint8, orig_uint8),
            'npcr': 0.0,  # No change
            'uaci': 0.0,  # No change
            'chi2': chi_square(orig_uint8),
            'mae': 0.0,  # No change
        }
        # Metrics for selective
        row_sel = {
            'patient': patient_id,
            'frame': frame_name,
            'type': 'selective',
            'psnr': psnr(orig_uint8, sel_uint8),
            'entropy': image_entropy(sel_uint8),
            'corr': correlation_coefficient(orig_uint8, sel_uint8),
            'npcr': npcr(orig_uint8, sel_uint8),
            'uaci': uaci(orig_uint8, sel_uint8),
            'chi2': chi_square(sel_uint8),
            'mae': mae(orig_uint8, sel_uint8),
        }
        # Metrics for full
        row_full = {
            'patient': patient_id,
            'frame': frame_name,
            'type': 'full',
            'psnr': psnr(orig_uint8, full_uint8),
            'entropy': image_entropy(full_uint8),
            'corr': correlation_coefficient(orig_uint8, full_uint8),
            'npcr': npcr(orig_uint8, full_uint8),
            'uaci': uaci(orig_uint8, full_uint8),
            'chi2': chi_square(full_uint8),
            'mae': mae(orig_uint8, full_uint8),
        }
        results.append(row_orig)
        results.append(row_sel)
        results.append(row_full)
    
    # Calculate averages
    averages = calculate_averages(results)
    
    # Write to CSV with range info as a comment row
    out_path = 'results/security_metrics.csv'
    header = ['patient','frame','type','psnr','entropy','corr','npcr','uaci','chi2','mae']
    # Ranges: PSNR: [0, inf], Entropy: [0, 8], Corr: [-1, 1], NPCR: [0, 100], UACI: [0, 100], Chi2: [0, inf], MAE: [0, 255]
    range_comment = ['# Ranges:', '', '', 'PSNR[0,inf]', 'Entropy[0,8]', 'Corr[-1,1]', 'NPCR[0,100]', 'UACI[0,100]', 'Chi2[0,inf]', 'MAE[0,255]']
    
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(range_comment)
        writer.writerow(header)
        
        # Write individual results
        for row in results:
            writer.writerow([row[h] for h in header])
        
        # Add empty row for separation
        writer.writerow([])
        writer.writerow(['# AVERAGES ACROSS ALL PATIENTS'])
        
        # Write averages
        for enc_type in ['original', 'selective', 'full']:
            if enc_type in averages:
                avg_row = averages[enc_type]
                writer.writerow([avg_row[h] for h in header])
    
    print(f"Done. Results saved to {out_path}")
    
    # Print summary to console
    print("\n=== AVERAGE METRICS SUMMARY ===")
    for enc_type in ['original', 'selective', 'full']:
        if enc_type in averages:
            avg = averages[enc_type]
            print(f"\n{enc_type.upper()} ENCRYPTION:")
            print(f"  Entropy: {avg['entropy']:.3f}")
            print(f"  Correlation: {avg['corr']:.3f}")
            print(f"  NPCR: {avg['npcr']:.2f}%")
            print(f"  UACI: {avg['uaci']:.2f}%")
            print(f"  Chi-Square: {avg['chi2']:.2f}")
            print(f"  MAE: {avg['mae']:.2f}")
            if avg['psnr'] != '-':
                print(f"  PSNR: {avg['psnr']:.2f}")

if __name__ == '__main__':
    evaluate_all() 
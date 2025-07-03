# 🛡️ Selective Encryption for Medical Images (ACDC Cardiac MRI)

This project implements **selective encryption** on cardiac MRI volumes from the **ACDC dataset**, where **regions of interest (ROIs)** (e.g., myocardium, left ventricle, right ventricle) are encrypted using **AES**, while **non-ROI regions** are encrypted using **ChaCha20**. The performance is compared to full AES encryption of the entire image.

---

## 🎯 Objective

- Enhance **privacy** in medical imaging while reducing **computational overhead**.
- Encrypt only sensitive **ROI labels** (1: LV, 2: RV, 3: Myocardium) with **AES**.
- Use **ChaCha20** for non-ROI to maintain performance.
- Compare **encryption time** between selective encryption and full AES encryption.

---

## ⚙️ How It Works

1. Load 3D cardiac MRI volumes and corresponding ground-truth segmentation masks.
2. Identify ROIs based on mask labels.
3. Apply:
   - **AES (CBC mode)** to encrypt ROI voxels.
   - **ChaCha20** stream cipher for non-ROI voxels.
4. Optionally save encrypted volumes.
5. Measure and compare:
   - ⏱️ Full AES encryption time
   - ⏱️ Selective AES + ChaCha20 encryption time

---

## 🚀 Getting Started

### 1. Installation
Install all required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Data Structure
The code expects the following directory structure for input data:
```
Data/Original/
  ├── patient001/
  │     ├── patient001_frame01.nii.gz
  │     ├── patient001_frame01_gt.nii.gz
  │     └── ...
  ├── patient002/
  │     └── ...
  └── ...
```
Each patient folder should contain `.nii.gz` images and corresponding `_gt.nii.gz` segmentation masks.

### 3. Configuration
- Encryption keys and IVs are generated randomly at runtime (see `src/config.py`).
- No manual key setup is required for basic runs, but for reproducibility, you may want to set fixed keys in `src/config.py`.

---

## ⚙️ Running the Project

### A. Batch Processing (Command Line)
To process all patients and log timing results:
```bash
python src/main.py
```
- Results (timing, logs, encrypted images) are saved in the `results/` directory.

### B. Interactive Web App (Streamlit)
To launch the Streamlit app for selective encryption and visualization:
```bash
streamlit run src/streamlit_app.py
```
- Choose to process all, a specific, or the first N patients.
- Run multiple trials for timing averages.
- Visualize sample encrypted images and view timing results in a table.

### C. Evaluating Security Metrics
After encryption, you can quantitatively assess the security of the encrypted images using a suite of standard metrics:
- **PSNR** (Peak Signal-to-Noise Ratio): Lower is better (more difference from original).
- **Entropy**: Higher is better (more randomness).
- **Correlation**: Closer to 0 is better (less similarity).
- **NPCR** (Number of Pixels Change Rate): Higher is better (more pixels changed).
- **UACI** (Unified Average Changing Intensity): Higher is better (greater intensity change).
- **Chi-Square**: Higher is better (more uniform/random distribution).
- **MAE** (Mean Absolute Error): Higher is better (greater difference).

To run the evaluation and generate a CSV report:
```bash
python src/evaluate_security.py
```
- Results are saved to `results/security_metrics.csv`.
- The script prints a summary of average metrics to the console for quick comparison between original, selective, and full encryption.

---

## 🖼️ Demonstration

Below is a demonstration of the selective encryption process:

![Demonstration of encryption](results/Demonstration.png)

---

## 📊 Experimental Setup & Results

- Experiments were conducted on **150 patients** dataset and sometimes looped over patients more than once, using **both frames (frame01 and frame02)** for each patient.
- The results, including encrypted outputs and timing logs, are saved in the `results/` directory.
- The **selective encryption approach showed a 60–70% performance improvement** (faster encryption time) compared to full AES encryption, while maintaining ROI protection.

---

## ✅ Key Benefits

- 🔒 **Privacy-preserving**: Heavily Encrypts only the medically relevant regions and light weight the rest.
- ⚡ **Faster performance**: Avoids full AES image encryption when unnecessary.
- 📁 **Result tracking**: Timing logs, security measures and encrypted volumes are organized and saved.
- 🧠 **Adaptable**: Easily extendable to other medical datasets with segmentation labels.

---

## 👨‍💻 Developed By

**Mohamed Hafez**  
Researcher & AI Engineer

Inspired by real-world challenges in privacy-preserving AI for healthcare.

---

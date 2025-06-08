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

## 📊 Experimental Setup & Results

- Experiments were conducted on **150 patients** and sometimes looped over patients more than once, using **both frames (frame01 and frame02)** for each patient.
- The results, including encrypted outputs and timing logs, are saved in the `results/` directory.
- The **selective encryption approach showed a 60–70% performance improvement** (faster encryption time) compared to full AES encryption, while maintaining ROI protection.

---

## ✅ Key Benefits

- 🔒 **Privacy-preserving**: Encrypts only the medically relevant regions.
- ⚡ **Faster performance**: Avoids full image encryption when unnecessary.
- 📁 **Result tracking**: Timing logs and encrypted volumes are organized and saved.
- 🧠 **Adaptable**: Easily extendable to other medical datasets with segmentation labels.

---

## 👨‍💻 Developed By

**Mohamed Hafez**  
Researcher & AI Engineer

Inspired by real-world challenges in privacy-preserving AI for healthcare.

---

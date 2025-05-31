# Selective-Encryption# 🧠 Selective Encryption for Medical Images (ACDC Cardiac MRI)

This project applies **selective encryption** to cardiac MRI data from the **ACDC dataset**, encrypting **regions of interest (ROI)** using **AES** and **non-ROI** using **ChaCha20**, then compares the performance to full AES encryption of the entire image.

---



## 🔍 Objective

- **Selective encryption** aims to protect only the most sensitive regions (e.g., myocardium, LV, RV) of medical images to reduce computational cost while preserving privacy.
- **Full AES encryption** is used as a baseline for comparison.
- The project compares **encryption time** between selective and full approaches.

---

## 🛠️ How It Works

1. Load 3D cardiac MRI volumes and their corresponding segmentation masks.
2. Identify ROI using label values (e.g., 1: LV, 2: RV, 3: Myocardium).
3. Encrypt ROI voxels with **AES (CBC mode)** and non-ROI voxels with **ChaCha20**.
4. Optionally save encrypted volumes to disk.
5. Record and compare encryption times for:
   - Full AES encryption
   - Selective AES + ChaCha20 encryption

---

Developed by Mohamed Hafez, Biomedical & AI Engineer

Inspired by the need for privacy-preserving medical imaging and performance-efficient encryption schemes.

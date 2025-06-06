import streamlit as st
import os
import pandas as pd
from processing import process_patient_folder, log_avg, process_single_patient
from utils import get_patient_ids

BASE_DIR = "Data/Original"
OUTPUT_DIR = "results/encrypted"
LOG_FILE = "results/timing_reports/timing_log.csv"

st.title("Selective Encryption of Medical Images")

# Load patient IDs
patient_ids = get_patient_ids(BASE_DIR)

# User selects processing option
selection_option = st.radio(
    "Choose processing mode:",
    ["All Patients", "Specific Patient", "First N Patients"]
)

selected_patient = None
num_patients = None

if selection_option == "Specific Patient":
    selected_patient = st.selectbox("Select Patient ID", options=patient_ids)
elif selection_option == "First N Patients":
    num_patients = st.number_input("Enter number of patients to process", min_value=1, max_value=len(patient_ids), step=1)

num_runs = st.number_input("Number of runs (to average timings)", min_value=1, max_value=10, value=1, step=1)

run_button = st.button("Run Encryption Trial")

if run_button:
    total_sel_times = []
    total_full_times = []
    total_processed_patients = 0

    for run_idx in range(num_runs):
        st.write(f"--- Run {run_idx + 1} of {num_runs} ---")

        all_selective_times = []
        all_full_times = []

        if selection_option == "All Patients":
            patients_to_process = patient_ids
        elif selection_option == "First N Patients":
            patients_to_process = patient_ids[:num_patients]
        elif selection_option == "Specific Patient":
            patients_to_process = [selected_patient]
        st.write(f"Processing")

        for pid in patients_to_process:
            sel_times, full_times = process_single_patient(os.path.join(BASE_DIR, pid), pid)
            all_selective_times.extend(sel_times)
            all_full_times.extend(full_times)

        total_processed_patients = len(patients_to_process)

        # Accumulate times across runs
        total_sel_times.extend(all_selective_times)
        total_full_times.extend(all_full_times)

        avg_sel = sum(all_selective_times) / len(all_selective_times) if all_selective_times else 0
        avg_full = sum(all_full_times) / len(all_full_times) if all_full_times else 0
        st.success(f"Run {run_idx + 1} processed {total_processed_patients} patients. Avg selective time: {avg_sel:.5f}s, Avg full time: {avg_full:.5f}s")

    # Overall averages across all runs
    overall_avg_sel = sum(total_sel_times) / len(total_sel_times) if total_sel_times else 0
    overall_avg_full = sum(total_full_times) / len(total_full_times) if total_full_times else 0

    st.subheader("Overall Average Timing After All Runs")
    st.write(f"Processed {total_processed_patients} patients per run, over {num_runs} runs")
    st.write(f"Overall Avg Selective Encryption Time: {overall_avg_sel:.5f} s")
    st.write(f"Overall Avg Full Encryption Time:       {overall_avg_full:.5f} s")

    # Log overall average
    log_row = log_avg(LOG_FILE, overall_avg_sel, overall_avg_full, total_processed_patients*num_runs)

    # Display who is faster overall
    if overall_avg_sel < overall_avg_full:
        diff_pct = ((overall_avg_full - overall_avg_sel) / overall_avg_full) * 100
        st.info(f"Selective encryption is faster by {diff_pct:.2f}%")
    else:
        diff_pct = ((overall_avg_sel - overall_avg_full) / overall_avg_sel) * 100
        st.info(f"Full encryption is faster by {diff_pct:.2f}%")

    # Show log summary as DataFrame (using data returned from log_avg)
    df = pd.DataFrame(
        [log_row],
        columns=["trial", "Selective", "Full", "Faster", "(%)", "patients"]
    )
    st.subheader("Run Summary Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

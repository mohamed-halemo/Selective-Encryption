import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style for better-looking plots
plt.style.use('bmh')  # Using a built-in style instead of seaborn
sns.set_theme()  # This will set seaborn's default theme

# Set default font sizes
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14
})

def load_and_prepare_data():
    # Load the timing log data
    df = pd.read_csv('results/timing_reports/timing_log.csv')
    
    # Convert percentage strings to float
    df['percentage_difference'] = df['percentage_difference'].str.rstrip('%').astype(float)
    
    # Convert times to milliseconds
    df['avg_selective_time'] = df['avg_selective_time'] * 1000
    df['avg_full_time'] = df['avg_full_time'] * 1000
    
    return df

def select_representative_trials(df):
    # Define target image counts we want to show
    target_counts = [10, 30, 50, 70, 90, 110, 130, 150]
    
    # Find the closest trial to each target count
    selected_trials = []
    for target in target_counts:
        # Find the trial with the closest number of images to our target
        closest_trial = df.iloc[(df['num_processed'] - target).abs().argsort()[0]]
        selected_trials.append(closest_trial)
    
    # Convert to DataFrame and sort by number of images
    selected_df = pd.DataFrame(selected_trials)
    selected_df = selected_df.sort_values('num_processed')
    
    return selected_df

def create_patient_comparison_chart(df):
    # Create a new figure with extra space at the bottom for summary
    plt.figure(figsize=(15, 10))
    
    # Create main plot area with extra space at bottom
    plt.subplot2grid((5, 1), (0, 0), rowspan=4)
    
    # Select representative trials
    df_subset = select_representative_trials(df)
    
    # Create x-axis positions for the bars
    x = np.arange(len(df_subset))
    width = 0.35
    
    # Create bars
    selective_bars = plt.bar(x - width/2, df_subset['avg_selective_time'], 
                           width, label='Selective (AES+ChaCha20)',
                           color='#2ecc71', alpha=0.8)
    full_bars = plt.bar(x + width/2, df_subset['avg_full_time'], 
                       width, label='Full AES',
                       color='#e74c3c', alpha=0.8)
    
    # Add labels and title
    plt.xlabel('Patients Processed', fontsize=25, labelpad=10)
    plt.ylabel('Encryption Time (milliseconds)', fontsize=25, labelpad=10)
    plt.title('Time Comparison', fontsize=30, pad=20)
    
    # Add only image counts as x-tick labels
    plt.xticks(x, [f'{int(df_subset.iloc[i]["num_processed"])} Patients' 
                   for i in range(len(df_subset))], rotation=45, fontsize=14)
    
    # Add legend with larger font
    plt.legend(fontsize=14, loc='upper left')
    
    # Add grid for better readability
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Create summary subplot
    plt.subplot2grid((5, 1), (4, 0))
    plt.axis('off')  # Turn off axis
    
    # Add summary statistics in a table format
    # summary_data = [
    #     ['Metric', 'Value'],
    #     ['Average Selective Time', f"{df_subset['avg_selective_time'].mean():.2f} ms"],
    #     ['Average Full AES Time', f"{df_subset['avg_full_time'].mean():.2f} ms"],
    #     ['Mean Performance Improvement', f"{df_subset['percentage_difference'].mean():.1f}%"],
    #     ['Total Images Processed', f"{df_subset['num_processed'].sum():,}"],
    #     ['Average Images per Trial', f"{df_subset['num_processed'].mean():.1f}"]
    # ]
    
    # Create table with larger font
    # table = plt.table(
    #                  loc='center',
    #                  cellLoc='center',
    #                  colWidths=[0.6, 0.4])
    
    # # Style the table
    # table.auto_set_font_size(False)
    # table.set_fontsize(14)  # Increased font size
    # table.scale(1, 1.5)
    
    # Style header row
    # for i in range(2):
    #     table[(0, i)].set_facecolor('#404040')
    #     table[(0, i)].set_text_props(color='white', weight='bold')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('results/patient_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Load and prepare data
    df = load_and_prepare_data()
    
    # Create patient comparison chart
    create_patient_comparison_chart(df)
    
    # Print summary statistics
    df_subset = select_representative_trials(df)
    print("\nPatient Comparison Summary (Selected Trials):")
    print(f"Average Selective Encryption Time: {df_subset['avg_selective_time'].mean():.2f} ms")
    print(f"Average Full AES Time: {df_subset['avg_full_time'].mean():.2f} ms")
    print(f"Mean Performance Improvement: {df_subset['percentage_difference'].mean():.1f}%")
    print(f"Total Images Processed: {df_subset['num_processed'].sum():,}")
    print(f"Average Images per Trial: {df_subset['num_processed'].mean():.1f}")
    
    # Print the selected image counts
    print("\nSelected Image Counts:")
    for count in df_subset['num_processed']:
        print(f"- {int(count)} images")

if __name__ == "__main__":
    main() 
import pandas as pd

# File paths
file1 = r'cleaned-mat-data-withG12.csv'
file2 = r'cleaned-por-data-withG12.csv'
output_file = r'combined-data-withG12.csv'

# Read both CSV files
mat_df = pd.read_csv(file1)
por_df = pd.read_csv(file2)

# Combine the dataframes
combined_df = pd.concat([mat_df, por_df], ignore_index=True)

# Save to new CSV
combined_df.to_csv(output_file, index=False)

print(f"Combined CSV saved to: {output_file}")

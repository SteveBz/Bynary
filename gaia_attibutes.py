import os
import pandas as pd
from astroquery.gaia import Gaia
import logging
import time
import numpy as np

logging.basicConfig(level=logging.DEBUG)

# Define parameters
input_csv = "LAMOST_Gaia.csv"  # Update this with your input CSV filename
output_csv = "gaia_results.csv"
batch_size = 1000  # Number of source IDs per query

# Login to Gaia
Gaia.login(user="scookson", password="Esa.4142135")

# Read input CSV (assuming it has a column named 'source_id')
df_input = pd.read_csv(input_csv, dtype={'source_id': str})  # Ensure IDs are treated as strings

# Dictionary to store results
results_dict = {}

# Open output file and write headers
#with open(output_csv, 'w') as f:
#    f.write("source_id,ipd_frac_multi_peak\n")  # Modify headers based on the expected output

# Process the source IDs in batches
for i in range(0, len(df_input), batch_size):
    batch = df_input['source_id'][i:i + batch_size].tolist()

    # Convert the list of source IDs to a string format for SQL
    source_ids_str = ', '.join(map(str, batch))

    # Define the query with the IN clause for source_id
    query = f'''
    SELECT source_id, ipd_frac_multi_peak
    FROM gaiadr3.gaia_source
    WHERE source_id IN ({source_ids_str})
    AND parallax IS NOT NULL
    '''

    # Print the query for debugging
    if i<=batch_size*10:
        print("Executing query:\n", query)

    try:
        # Use async job execution to prevent timeouts
        job = Gaia.launch_job_async(query, dump_to_file=False)
        data = job.get_results()

        # Ensure we have results before proceeding
        if len(data) == 0:
            print(f"No data found for batch {i // batch_size + 1}.")
            continue

        # Convert to Pandas DataFrame and standardize column names
        df_result = data.to_pandas()
        df_result.columns = [col.lower() for col in df_result.columns]  # Ensure lowercase column names

        # Check if expected columns exist
        if 'source_id' not in df_result.columns or 'ipd_frac_multi_peak' not in df_result.columns:
            print(f"Warning: Unexpected columns in batch {i // batch_size + 1}: {df_result.columns}")
            continue
        # Append results to output CSV
        #data.to_pandas().to_csv(output_csv, mode='a', header=False, index=False)
                # Store results in a dictionary for sorting later
        for _, row in df_result.iterrows():
            results_dict[row['source_id']] = row['ipd_frac_multi_peak']
        print(f"Batch {i // batch_size + 1} processed successfully.")
    except Exception as e:
        print(f"Error in batch {i // batch_size + 1}: {e}")


    # Sleep to avoid hitting API limits
    #time.sleep()  # Adjust if needed
    #print(results_dict)
# Ensure output is in the same order as input
df_output = df_input[['source_id']].copy()  # Keep only source_id column
#df_output['ipd_frac_multi_peak'] = df_output['source_id'].map(results_dict)
# Save to CSV
#df_output.to_csv(output_csv, index=False)
#print(f"Data saved to {output_csv}")


# Convert dictionary keys to strings (to match DataFrame)
results_dict = {str(k): v if pd.notna(v) else np.nan for k, v in results_dict.items()}

# Ensure source_id is treated as a string before mapping
df_output['ipd_frac_multi_peak'] = df_output['source_id'].astype(str).map(results_dict)

# Save to CSV
df_output.to_csv(output_csv, index=False)
print(f"Data saved to {output_csv}")

import rasterio
import numpy as np
import pandas as pd
import os

# Define the directory containing the input TIFF files
input_directory = r'C:\Users\Jayant\Desktop\WFP\Extracted'

# Define the directory to save the output TIFF files
output_directory = r'C:\Users\Jayant\Desktop\WFP\Output'

# Helper function to get the dekad from the day part of the filename
def get_dekad(day_str):
    if day_str == 'd1':
        return 'dekad1'
    elif day_str == 'd2':
        return 'dekad2'
    elif day_str == 'd3':
        return 'dekad3'
    else:
        return None

# Initialize lists to store data
dekad1_data = []
dekad2_data = []
dekad3_data = []

# Loop through all TIFF files in the input directory
for file in os.listdir(input_directory):
    if file.endswith('.tif') and file.startswith('mozrfb'):
        file_path = os.path.join(input_directory, file)
        
        # Extract the year, month, and day part from the file name
        year = file[6:10]
        month = file[10:12]
        day_part = file[12:14]  # Extracts 'd1', 'd2', or 'd3'
        
        # Check if the file belongs to March
        if month == '03':
            with rasterio.open(file_path) as src:
                # Read the raster data
                raster_data = src.read(1)
                
                # Get dekad based on day part
                dekad = get_dekad(day_part)
                
                # Append the data to the appropriate dekad list
                if dekad == 'dekad1':
                    dekad1_data.append(raster_data)
                elif dekad == 'dekad2':
                    dekad2_data.append(raster_data)
                elif dekad == 'dekad3':
                    dekad3_data.append(raster_data)
                
                # Debugging: Print file details
                print(f"Processed file: {file}")
                print(f"Year: {year}, Month: {month}, Day part: {day_part}")
                print(f"Dekad: {dekad}")

# Function to compute the 95th percentile
def compute_95th_percentile(data_list):
    if not data_list:
        raise ValueError("No data available for this dekad.")
    # Stack the data along a new axis and compute the 95th percentile along that axis
    data_stack = np.stack(data_list, axis=0)
    percentile_95 = np.percentile(data_stack, 95, axis=0)
    return percentile_95

# Save the results as new TIFF files in the output directory
def save_raster(data, reference_file, output_file):
    with rasterio.open(reference_file) as src:
        meta = src.meta
    meta.update(dtype=rasterio.float32)
    with rasterio.open(output_file, 'w', **meta) as dst:
        dst.write(data.astype(rasterio.float32), 1)

# Compute the 95th percentile for each dekad
if dekad1_data:
    dekad1_percentile_95 = compute_95th_percentile(dekad1_data)
    output_file1 = os.path.join(output_directory, 'dekad1_percentile_95.tif')
    save_raster(dekad1_percentile_95, os.path.join(input_directory, os.listdir(input_directory)[0]), output_file1)
    print(f"Dekad 1 percentile saved to: {output_file1}")
else:
    print("No data found for dekad 1.")

if dekad2_data:
    dekad2_percentile_95 = compute_95th_percentile(dekad2_data)
    output_file2 = os.path.join(output_directory, 'dekad2_percentile_95.tif')
    save_raster(dekad2_percentile_95, os.path.join(input_directory, os.listdir(input_directory)[0]), output_file2)
    print(f"Dekad 2 percentile saved to: {output_file2}")
else:
    print("No data found for dekad 2.")

if dekad3_data:
    dekad3_percentile_95 = compute_95th_percentile(dekad3_data)
    output_file3 = os.path.join(output_directory, 'dekad3_percentile_95.tif')
    save_raster(dekad3_percentile_95, os.path.join(input_directory, os.listdir(input_directory)[0]), output_file3)
    print(f"Dekad 3 percentile saved to: {output_file3}")
else:
    print("No data found for dekad 3.")

print("95th percentile rainfall data saved successfully.")

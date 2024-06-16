import rasterio
import numpy as np
from rasterstats import zonal_stats
import os
import json
from affine import Affine
import geopandas as gpd
from shapely.geometry import mapping

# Define the directory containing the input TIFF files
input_directory = r'C:\Users\Jayant\Desktop\WFP\Extracted'

# Define the path to the GeoJSON file containing the administrative boundary
geojson_file = r'C:\Users\Jayant\Desktop\WFP\geoBoundaries-MOZ-ADM2.geojson'

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

# Load the GeoJSON file
with open(geojson_file) as f:
    geojson_data = json.load(f)

# Get the affine transform from a sample raster file
sample_raster_file = os.path.join(input_directory, os.listdir(input_directory)[0])
with rasterio.open(sample_raster_file) as src:
    affine_transform = src.transform

# Initialize lists to store data
dekad1_data = []
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
                # Read the raster data and apply the affine transform
                raster_data = src.read(1)
                raster_data_affine = rasterio.transform.array_bounds(
                    src.height, src.width, src.transform)
                
                # Get dekad based on day part
                dekad = get_dekad(day_part)
                
                # Append the data to the appropriate dekad list
                if dekad == 'dekad1':
                    dekad1_data.append(raster_data)
                elif dekad == 'dekad3':
                    dekad3_data.append(raster_data)

# Function to compute the 95th percentile
def compute_95th_percentile(data_list):
    if not data_list:
        raise ValueError("No data available for this dekad.")
    # Stack the data along a new axis and compute the 95th percentile along that axis
    data_stack = np.stack(data_list, axis=0)
    percentile_95 = np.percentile(data_stack, 95, axis=0)
    return percentile_95

# Compute the 95th percentile for dekad 1 and 3
dekad1_percentile_95 = compute_95th_percentile(dekad1_data)
dekad3_mean = np.mean(dekad3_data, axis=0)

# Compute zonal statistics for the administrative boundary
stats_dekad1 = zonal_stats(geojson_data, dekad1_percentile_95, affine=affine_transform, stats=['mean'])
stats_dekad3 = zonal_stats(geojson_data, dekad3_mean, affine=affine_transform, stats=['mean'])

# Create GeoDataFrame for dekad 1
stats_dekad1_df = gpd.GeoDataFrame.from_features(geojson_data)
stats_dekad1_df['mean_rainfall_dekad1'] = [stats_dekad1[0]['mean']] * len(stats_dekad1_df)

# Create GeoDataFrame for dekad 3
stats_dekad3_df = gpd.GeoDataFrame.from_features(geojson_data)
stats_dekad3_df['mean_rainfall_dekad3'] = [stats_dekad3[0]['mean']] * len(stats_dekad3_df)

# Save GeoDataFrames to vector files
output_directory = r'C:\Users\Jayant\Desktop\WFP\Output'

output_file_dekad1 = os.path.join(output_directory, 'mean_rainfall_dekad1.shp')
stats_dekad1_df.to_file(output_file_dekad1)

output_file_dekad3 = os.path.join(output_directory, 'mean_rainfall_dekad3.shp')
stats_dekad3_df.to_file(output_file_dekad3)

print("Output saved successfully in vector format.")

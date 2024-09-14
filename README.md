# Sentinel1_download
Description
This script downloads Sentinel-1 Ground Range Detected (GRD) data for both VV and VH polarizations, 
as well as the incidence angle, for ascending and descending orbits.
It processes the data for a user-defined area of interest (AOI) and a specific time range. 
The results are exported as CSV files containing the mean values of the polarizations over the defined 
polygons. 
The script utilizes Google Earth Engine (GEE) and the geemap Python package to manage the Earth Engine API.

Features
Downloads Sentinel-1 GRD data from Google Earth Engine.
Processes VV, VH, and incidence angle bands.
Handles both ascending and descending orbit passes.
Extracts mean values for each polarization over user-defined polygons (from shapefiles).
Saves the processed data as CSV files.
Supports batch processing by handling large shapefiles in chunks.

Requirements
Python 3.x
Google Earth Engine (GEE) Python API
geopandas, pandas, geemap, and tqdm libraries

How to Use
Install the required dependencies.
Set the following variables in the script:
extent_gee: Path to the geographic region in GEE (AOI).
path_GEE: Path to a GEE FeatureCollection containing the polygons you want to analyze.
shapefile_path: Local path to the shapefile containing the polygons of interest.
raw_output_path: Path where the output CSV files will be saved.
Run the script to process the Sentinel-1 data for the specified date range and polygons.

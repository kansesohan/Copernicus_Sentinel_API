import os
import json
import shutil
import zipfile
from sentinelsat import SentinelAPI, geojson_to_wkt

# Set up API credentials and desired download folder
user = 'kansesohan'
password = 'GISsohan'
download_folder = r'E:\Crop_Water_Stress_Condition_Western_Maharashtra\RemoteSensingData\1.Raw'

# Define the GeoJSON file path
geojson_path = r'E:\Crop_Water_Stress_Condition_Western_Maharashtra\Annexure_Data\S2A_Tiles.geojson'

# Connect to the Sentinel API
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

# Create the folder structure based on tile, year, and month
def create_folder_structure(folder_path, tile_name, year, month):
    tile_folder = os.path.join(folder_path, tile_name)
    year_folder = os.path.join(tile_folder, str(year))
    month_folder = os.path.join(year_folder, str(month))
    os.makedirs(month_folder, exist_ok=True)
    return month_folder

# Extract specific files from the zip folder
def extract_files(zip_path, destination_folder, file_extensions):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if any(file.endswith(ext) for ext in file_extensions):
                zip_ref.extract(file, destination_folder)

# Read the GeoJSON file and extract tile names
def get_tile_names(geojson_path):
    tile_names = []
    with open(geojson_path) as f:
        data = json.load(f)
        for feature in data['features']:
            tile_names.append(feature['properties']['Name'])
    return tile_names

# Download and store the Sentinel data
tile_names = get_tile_names(geojson_path)
for tile_name in tile_names:
    print(f"Downloading data for {tile_name}...")
    
    # Iterate over the desired time period, e.g., from January 2018 to December 2018
    for year in range(2019, 2020):
        for month in range(1, 2):
            # Create the folder structure
            month_folder = create_folder_structure(download_folder, tile_name, year, month)
            
            # Define the search parameters
            with open(geojson_path) as f:
                geojson_obj = json.load(f)
            footprint = geojson_to_wkt(geojson_obj)
            start_date = f'{year}{month:02d}01'
            end_date = f'{year}{month:02d}28'
            
            # Search for available products
            products = api.query(footprint, date=(start_date, end_date), platformname='Sentinel-2', producttype='S2MSI1C', cloudcoverpercentage=(0, 30), filename=f'*{tile_name}*')
            
            # Download the products
            downloaded_files = api.download_all(products, directory_path=month_folder)
            
            # Extract the desired files and delete the remaining ones
            for file_info in downloaded_files:
                file_path = file_info.get('path') or file_info.get('file_path')
                if file_path:
                    zip_folder = os.path.join(month_folder, os.path.basename(file_path))
                    extract_files(zip_folder, month_folder, ['.jp2', '.tiff'])  # Adjust the file extensions as needed
                    shutil.rmtree(zip_folder)  # Delete the remaining files
            
            print(f"Downloaded and processed data for {tile_name} - Year: {year}, Month: {month}")




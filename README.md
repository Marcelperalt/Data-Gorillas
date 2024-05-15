
Climate Data Processor
This repository contains scripts to process and extract climate data from NetCDF files and retrieve air quality station information for various cities.

Table of Contents
Installation
Usage
Climate Data Extraction
Air Quality Stations Retrieval
Scripts
License
Installation
Clone the repository:

sh
Code kopieren
git clone https://github.com/yourusername/climate-data-processor.git
cd climate-data-processor
Install dependencies:

sh
Code kopieren
pip install -r requirements.txt
Usage
Climate Data Extraction
The script climate_data_extractor.py processes NetCDF files to extract climate data for specified regions and saves the data as CSV files.

Define the coordinates for your regions of interest in the main section:

python
Code kopieren
coords = {
    'Istanbul': (41.3, 28.6, 40.8, 29.3),
    'Paris': (49.1, 1.8, 48.5, 3.0),
    'Madrid': (40.8, -4.0, 40.0, -3.4),
    'London': (51.7, -0.6, 51.2, 0.4),
    'Hamburg': (53.8, 9.6, 53.2, 10.5)
}
Set the directory containing your NetCDF files and the starting date for data extraction:

python
Code kopieren
processor = NetCDFProcessor(netcdf_dir='netcdf4data', coords=coords)
processor.process_all(starting_date='2013-01-01')
Run the script:

sh
Code kopieren
python climate_data_extractor.py
Air Quality Stations Retrieval
The script air_quality_stations.py retrieves air quality station data for specified cities using the WAQI API and saves the data to a text file.

Set your list of cities and API token in the script:

python
Code kopieren
cities = ["Paris", "Hamburg", "Istanbul", "Madrid", "London"]
token = "your_api_token_here"
Run the script:

sh
Code kopieren
python air_quality_stations.py
Scripts
climate_data_extractor.py
This script extracts climate data from NetCDF files for specific geographic regions and saves the data as CSV files.

Classes:
DataExtractor: Handles loading and extracting data from a NetCDF file.
RegionalDataExtractor: Extends DataExtractor to handle specific geographic regions.
NetCDFProcessor: Processes multiple NetCDF files for defined regions.
air_quality_stations.py
This script retrieves air quality station information from the WAQI API for specified cities and saves the data to a text file.

License
This project is licensed under the MIT License - see the LICENSE file for details.

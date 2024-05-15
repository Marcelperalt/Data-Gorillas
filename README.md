# Climate Data Processor

This repository contains scripts to process and extract climate data from NetCDF files and verify the extracted data against the original NetCDF files.

## Table of Contents

- [Usage](#usage)
  - [Climate Data Extraction](#climate-data-extraction)
  - [Data Verification](#data-verification)
- [Scripts](#scripts)
- [License](#license)

## Usage

### Climate Data Extraction

The script `netcdf_to_csv.py` processes NetCDF files to extract climate data for specified regions and saves the data as CSV files.

1. **Define the coordinates for your regions of interest in the main section:**

   ```python
   #'City': (nw_lat, nw_lon, se_lat, se_lon):
   coords = {
       'Istanbul': (41.3, 28.6, 40.8, 29.3),
       'Paris': (49.1, 1.8, 48.5, 3.0),
       'Madrid': (40.8, -4.0, 40.0, -3.4),
       'London': (51.7, -0.6, 51.2, 0.4),
       'Hamburg': (53.8, 9.6, 53.2, 10.5)
   }
   ```

2. **Set the directory containing your NetCDF files and the starting date for data extraction:**

   ```python
   processor = NetCDFProcessor(netcdf_dir='netcdf4data', coords=coords)
   processor.process_all(starting_date='2013-01-01')
   ```

3. **Run the script:**
   ```sh
   python netcdf_to_csv.py
   ```

### Data Verification

The script `netcdf_verifier.py` verifies the data extracted from NetCDF files against the generated CSV files.

1. **Set the coordinates and directories in the main section:**

   ```python
   coords = {
       'Paris': (49.1, 1.8, 48.5, 3.0),
   }

   netcdf_dir = 'netcdf4data'
   csv_dir = 'CSVClimateData'
   starting_date = '2013-01-01'
   ```

2. **Run the script:**
   ```sh
   python netcdf_verifier.py
   ```

## Scripts

### `netcdf_to_csv.py`

This script extracts climate data from NetCDF files for specific geographic regions and saves the data as CSV files.

#### Classes:

- `DataExtractor`: Handles loading and extracting data from a NetCDF file.
- `RegionalDataExtractor`: Extends `DataExtractor` to handle specific geographic regions.
- `NetCDFProcessor`: Processes multiple NetCDF files for defined regions.

### `netcdf_verifier.py`

This script verifies the data extracted from NetCDF files against the generated CSV files to ensure data integrity.

#### Classes:

- `NetCDFVerifier`: Verifies the extracted data against the original NetCDF data.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

"""
Climate Data Processor

This script processes and extracts climate data from NetCDF files and saves it as CSV files.
"""

from datetime import datetime
import os
import json
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date

# Change the working directory to the script's location
script_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(script_dir)

# Load configuration
with open(os.path.join(script_dir, '..', '..', 'config.json'), 'r') as config_file:
    config = json.load(config_file)


def generate_headers(lat_range, lon_range, dataset):
    """
    Generate headers for the CSV file based on latitude and longitude ranges.
    """
    headers = ['Date']
    latitudes = dataset.variables['latitude'][lat_range]
    longitudes = dataset.variables['longitude'][lon_range]
    for lat in latitudes:
        for lon in longitudes:
            headers.append(f"{lat:.1f}, {lon:.1f}")
    return headers


class DataExtractor:
    """
    Class to handle loading and extracting data from a NetCDF file.
    """

    def __init__(self, filepath, output_directory, output_filename):
        self.filepath = filepath
        self.output_directory = output_directory
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        self.output_filename = os.path.join(
            self.output_directory, output_filename)
        self.dataset = self.load_dataset()
        self.variable_name = self.detect_variable()

    def load_dataset(self):
        """
        Load the NetCDF dataset.
        """
        return Dataset(self.filepath, 'r')

    def detect_variable(self):
        """
        Detect the variable to extract from the NetCDF file.
        """
        for name, _ in self.dataset.variables.items():
            if name not in ['longitude', 'latitude', 'time']:
                return name

    def find_index(self, coordinate, coordinate_type='latitude'):
        """
        Find the index of the closest coordinate in the NetCDF file.
        """
        coords = self.dataset.variables[coordinate_type][:]
        if coordinate < coords.min() or coordinate > coords.max():
            raise ValueError(
                f"{coordinate_type} value {coordinate} out of bounds.")
        return np.argmin(np.abs(coords - coordinate))

    def extract_data(self, lat_range, lon_range, start_idx=None, end_idx=None):
        """
        Extract data from the NetCDF file for the specified latitude and longitude ranges.
        """
        if start_idx is not None and end_idx is not None:
            data = self.dataset.variables[self.variable_name][start_idx:end_idx,
                                                              lat_range, lon_range]
        elif start_idx is not None:
            data = self.dataset.variables[self.variable_name][start_idx:,
                                                              lat_range, lon_range]
        else:
            data = self.dataset.variables[self.variable_name][:,
                                                              lat_range, lon_range]
        return data.reshape(data.shape[0], -1)

    def extract_date(self, start_idx=None, end_idx=None):
        """
        Extract dates from the NetCDF file.
        """
        time_var = self.dataset.variables['time']
        if start_idx is not None and end_idx is not None:
            dates = num2date(
                time_var[start_idx:end_idx], units=time_var.units, calendar=time_var.calendar)
        elif start_idx is not None:
            dates = num2date(
                time_var[start_idx:], units=time_var.units, calendar=time_var.calendar)
        else:
            dates = num2date(
                time_var[:], units=time_var.units, calendar=time_var.calendar)
        return [date.strftime('%Y-%m-%d') for date in dates]

    def print_time_info(self, start_idx=None, end_idx=None):
        """
        Print the time range information from the NetCDF file.
        """
        time_var = self.dataset.variables['time']
        dates = num2date(time_var[:], units=time_var.units,
                         calendar='standard' if 'calendar' not in time_var.ncattrs() else time_var.calendar)
        if start_idx is not None and end_idx is not None:
            dates_subset = dates[start_idx:end_idx]
            print("First date in the subset:", dates_subset[0])
            print("Last date in the subset:", dates_subset[-1])
        elif start_idx is not None:
            dates_subset = dates[start_idx:]
            print("First date in the subset:", dates_subset[0])
            print("Last date in the subset:", dates_subset[-1])
        else:
            print("First date in dataset:", dates[0])
            print("Last date in dataset:", dates[-1])

    def save_to_csv(self, data, dates, headers):
        """
        Save the extracted data to a CSV file.
        """
        print(f"Shape of data: {data.shape}")
        print(f"Number of headers: {len(headers)}")
        if data.size == 0:
            raise ValueError(
                "No data to save. Data extraction failed or resulted in an empty dataset.")
        df = pd.DataFrame(data, columns=headers[1:])
        df.insert(0, 'Date', dates)
        df.to_csv(self.output_filename, index=False)
        print(f"Data saved to {self.output_filename}")


class RegionalDataExtractor(DataExtractor):
    """
    Class to handle data extraction for specific geographic regions.
    """

    def __init__(self, filepath, nw_lat, nw_lon, se_lat, se_lon, output_directory, output_filename='output.csv'):
        super().__init__(filepath, output_directory, output_filename)
        self.nw_lat = nw_lat
        self.nw_lon = nw_lon
        self.se_lat = se_lat
        self.se_lon = se_lon

    def get_lat_lon_indices(self):
        """
        Get the indices for the specified latitude and longitude ranges.
        """
        nw_lat_idx = self.find_index(self.nw_lat, 'latitude')
        nw_lon_idx = self.find_index(self.nw_lon, 'longitude')
        se_lat_idx = self.find_index(self.se_lat, 'latitude')
        se_lon_idx = self.find_index(self.se_lon, 'longitude')
        lat_range = slice(min(nw_lat_idx, se_lat_idx),
                          max(nw_lat_idx, se_lat_idx) + 1)
        lon_range = slice(min(nw_lon_idx, se_lon_idx),
                          max(nw_lon_idx, se_lon_idx) + 1)
        return lat_range, lon_range

    def process_data(self, starting_date=None, ending_date=None):
        """
        Process data for the specified date range and save it to a CSV file.
        """
        start_idx = None
        end_idx = None

        time_var = self.dataset.variables['time']
        dates = num2date(
            time_var[:], units=time_var.units, calendar=time_var.calendar)

        if starting_date is not None:
            start_date = datetime.strptime(starting_date, '%Y-%m-%d')
            if start_date < dates[0] or start_date > dates[-1]:
                raise ValueError(
                    f"Starting date {starting_date} out of dataset bounds.")
            start_idx = next(i for i, date in enumerate(
                dates) if date >= start_date)

        if ending_date is not None:
            end_date = datetime.strptime(ending_date, '%Y-%m-%d')
            if end_date < dates[0] or end_date > dates[-1]:
                raise ValueError(
                    f"Ending date {ending_date} out of dataset bounds.")
            end_idx = next(i for i, date in enumerate(
                dates) if date > end_date)

        self.print_time_info(start_idx, end_idx)
        lat_range, lon_range = self.get_lat_lon_indices()
        data = self.extract_data(lat_range, lon_range, start_idx, end_idx)
        dates = self.extract_date(start_idx, end_idx)
        headers = generate_headers(lat_range, lon_range, self.dataset)
        self.save_to_csv(data, dates, headers)


class NetCDFProcessor:
    """
    Class to process multiple NetCDF files for defined regions.
    """

    def __init__(self, netcdf_dir, coords):
        self.netcdf_dir = netcdf_dir
        self.coords = coords

    def process_all(self, starting_date=None, ending_date=None):
        """
        Process all NetCDF files in the directory.
        """
        print("Current working directory:", os.getcwd())
        netcdf_files = [f for f in os.listdir(
            self.netcdf_dir) if f.endswith('.nc')]
        for filename in netcdf_files:
            self.process_file(filename, starting_date, ending_date)

    def process_file(self, filename, starting_date, ending_date):
        """
        Process a single NetCDF file.
        """
        filepath = os.path.join(self.netcdf_dir, filename)
        try:
            _ = Dataset(filepath, 'r')
        except FileNotFoundError:
            print(f"File {filepath} not found. Skipping.")
            return
        variable_name = filename.split('_')[0]
        version = filename.split('_')[-1].replace('.nc', '')

        output_subdir = os.path.join(
            '..', '..', config['csv_dir'], variable_name)
        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)

        for city, (nw_lat, nw_lon, se_lat, se_lon) in self.coords.items():
            output_filename = f'{variable_name}_{city}_{version}.csv'
            city_extractor = RegionalDataExtractor(
                filepath=filepath,
                nw_lat=nw_lat,
                nw_lon=nw_lon,
                se_lat=se_lat,
                se_lon=se_lon,
                output_directory=output_subdir,
                output_filename=output_filename
            )
            city_extractor.process_data(
                starting_date=starting_date, ending_date=ending_date)


if __name__ == '__main__':
    processor = NetCDFProcessor(
        netcdf_dir=os.path.join('..', '..', config['netcdf_dir']),
        coords=config['city_coords']
    )
    processor.process_all(
        starting_date=config['starting_date'],
        ending_date=config['ending_date']
    )

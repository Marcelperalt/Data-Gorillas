"""
NetCDF Verifier

This script verifies the data extracted from NetCDF files against the CSV files generated from the same data.
"""

import os
from datetime import datetime
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date


class NetCDFVerifier:
    """
    Class to verify the data extracted from NetCDF files against CSV files.
    """

    def __init__(self, netcdf_dir, csv_dir, city_coords, starting_date):
        self.netcdf_dir = netcdf_dir
        self.csv_dir = csv_dir
        self.city_coords = city_coords
        self.starting_date = starting_date

    def load_csv_data(self, filepath):
        """
        Load data from a CSV file.
        """
        df = pd.read_csv(filepath)
        dates = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d').tolist()
        data = df.drop(columns=['Date']).values
        return dates, data

    def load_netcdf_data(self, filepath, variable_name, lat_range, lon_range, start_idx=None):
        """
        Load data from a NetCDF file.
        """
        dataset = Dataset(filepath, 'r')
        time_var = dataset.variables['time']
        if start_idx is not None:
            dates = num2date(
                time_var[start_idx:], units=time_var.units, calendar=time_var.calendar)
            data = dataset.variables[variable_name][start_idx:,
                                                    lat_range, lon_range]
        else:
            dates = num2date(
                time_var[:], units=time_var.units, calendar=time_var.calendar)
            data = dataset.variables[variable_name][:, lat_range, lon_range]
        dates = [date.strftime('%Y-%m-%d') for date in dates]
        data = data.reshape(data.shape[0], -1)
        return dates, data

    def find_index(self, dataset, coordinate, coordinate_type='latitude'):
        """
        Find the index of the closest coordinate in the NetCDF file.
        """
        coords = dataset.variables[coordinate_type][:]
        if coordinate < coords.min() or coordinate > coords.max():
            raise ValueError(
                f"{coordinate_type} value {coordinate} out of bounds.")
        return np.argmin(np.abs(coords - coordinate))

    def get_lat_lon_indices(self, dataset, nw_lat, nw_lon, se_lat, se_lon):
        """
        Get the indices for the specified latitude and longitude ranges.
        """
        nw_lat_idx = self.find_index(dataset, nw_lat, 'latitude')
        nw_lon_idx = self.find_index(dataset, nw_lon, 'longitude')
        se_lat_idx = self.find_index(dataset, se_lat, 'latitude')
        se_lon_idx = self.find_index(dataset, se_lon, 'longitude')
        lat_range = slice(min(nw_lat_idx, se_lat_idx),
                          max(nw_lat_idx, se_lat_idx) + 1)
        lon_range = slice(min(nw_lon_idx, se_lon_idx),
                          max(nw_lon_idx, se_lon_idx) + 1)
        return lat_range, lon_range

    def verify_data(self, netcdf_filepath, csv_filepath, nw_lat, nw_lon, se_lat, se_lon, variable_name):
        """
        Verify the data in the CSV file against the NetCDF file.
        """
        dataset = Dataset(netcdf_filepath, 'r')
        lat_range, lon_range = self.get_lat_lon_indices(
            dataset, nw_lat, nw_lon, se_lat, se_lon)

        start_idx = None
        if self.starting_date is not None:
            time_var = dataset.variables['time']
            dates = num2date(
                time_var[:], units=time_var.units, calendar=time_var.calendar)
            start_date = datetime.strptime(self.starting_date, '%Y-%m-%d')
            if start_date < dates[0] or start_date > dates[-1]:
                raise ValueError(
                    f"Starting date {self.starting_date} out of dataset bounds.")
            start_idx = next(i for i, date in enumerate(
                dates) if date >= start_date)

        csv_dates, csv_data = self.load_csv_data(csv_filepath)
        netcdf_dates, netcdf_data = self.load_netcdf_data(
            netcdf_filepath, variable_name, lat_range, lon_range, start_idx)

        # Check if dates match
        if csv_dates != netcdf_dates:
            print(f"Date mismatch: {csv_dates[0]} != {netcdf_dates[0]}")
            return False

        # Check if data matches and print sample comparisons
        if not np.allclose(csv_data, netcdf_data, atol=1e-6):
            print("Data mismatch found")
            mismatch_indices = np.where(
                ~np.isclose(csv_data, netcdf_data, atol=1e-6))
            for idx in zip(*mismatch_indices):
                print(
                    f"Mismatch at index {idx}: CSV data = {csv_data[idx]}, NetCDF data = {netcdf_data[idx]}")
            return False

        print("Data verification successful")
        return True

    def process_and_verify_files(self):
        """
        Process and verify all NetCDF and corresponding CSV files in the directories.
        """
        # Automatically list all NetCDF files in the directory
        netcdf_files = [f for f in os.listdir(
            self.netcdf_dir) if f.endswith('.nc')]

        for filename in netcdf_files:
            variable_name = filename.split('_')[0]
            version = filename.split('_')[-1].replace('.nc', '')

            for city, (nw_lat, nw_lon, se_lat, se_lon) in self.city_coords.items():
                netcdf_filepath = os.path.join(self.netcdf_dir, filename)
                csv_filepath = os.path.join(
                    self.csv_dir, variable_name, f'{variable_name}_{city}_{version}.csv')

                print(f'Verifying {csv_filepath} against {netcdf_filepath}...')
                self.verify_data(netcdf_filepath, csv_filepath,
                                 nw_lat, nw_lon, se_lat, se_lon, variable_name)


# Example usage
if __name__ == '__main__':
    COORDS = {
        # 'Istanbul': (41.3, 28.6, 40.8, 29.3),
        'Paris': (49.1, 1.8, 48.5, 3.0),
        # 'Madrid': (40.8, -4.0, 40.0, -3.4),
        # 'London': (51.7, -0.6, 51.2, 0.4),
        # 'Hamburg': (53.8, 9.6, 53.2, 10.5)
    }

    NETCDF_DIR = 'netcdf4data'
    CSV_DIR = 'CSVClimateData'
    STARTING_DATE = '2013-01-01'

    verifier = NetCDFVerifier(NETCDF_DIR, CSV_DIR, COORDS, STARTING_DATE)
    verifier.process_and_verify_files()

from datetime import datetime
from netCDF4 import Dataset, num2date
import numpy as np
import pandas as pd
import os


class DataExtractor:
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
        return Dataset(self.filepath, 'r')

    def detect_variable(self):
        for name, _ in self.dataset.variables.items():
            if name not in ['longitude', 'latitude', 'time']:
                return name

    def find_index(self, coordinate, coordinate_type='latitude'):
        coords = self.dataset.variables[coordinate_type][:]
        if coordinate < coords.min() or coordinate > coords.max():
            raise ValueError(
                f"{coordinate_type} value {coordinate} out of bounds.")
        return np.argmin(np.abs(coords - coordinate))

    def extract_data(self, lat_range, lon_range, start_idx=None):
        if start_idx is not None:
            data = self.dataset.variables[self.variable_name][start_idx:,
                                                              lat_range, lon_range]
        else:
            data = self.dataset.variables[self.variable_name][:,
                                                              lat_range, lon_range]
        return data.reshape(data.shape[0], -1)

    def extract_date(self, start_idx=None):
        time_var = self.dataset.variables['time']
        if start_idx is not None:
            dates = num2date(
                time_var[start_idx:], units=time_var.units, calendar=time_var.calendar)
        else:
            dates = num2date(
                time_var[:], units=time_var.units, calendar=time_var.calendar)
        return [date.strftime('%Y-%m-%d') for date in dates]

    def print_time_info(self, start_idx=None):
        time_var = self.dataset.variables['time']
        dates = num2date(time_var[:], units=time_var.units,
                         calendar='standard' if 'calendar' not in time_var.ncattrs() else time_var.calendar)
        if start_idx is not None:
            dates_subset = dates[start_idx:]
            print("First date in the subset:", dates_subset[0])
            print("Last date in the subset:", dates_subset[-1])
        else:
            print("First date in dataset:", dates[0])
            print("Last date in dataset:", dates[-1])

    def save_to_csv(self, data, dates):
        if data.size == 0:
            raise ValueError(
                "No data to save. Data extraction failed or resulted in an empty dataset.")
        df = pd.DataFrame(data)
        df.insert(0, 'Date', dates)
        df.to_csv(self.output_filename, index=False)
        print(f"Data saved to {self.output_filename}")


class RegionalDataExtractor(DataExtractor):
    def __init__(self, filepath, nw_lat, nw_lon, se_lat, se_lon, output_directory, output_filename='output.csv'):
        super().__init__(filepath, output_directory, output_filename)
        self.nw_lat = nw_lat
        self.nw_lon = nw_lon
        self.se_lat = se_lat
        self.se_lon = se_lon

    def get_lat_lon_indices(self):
        nw_lat_idx = self.find_index(self.nw_lat, 'latitude')
        nw_lon_idx = self.find_index(self.nw_lon, 'longitude')
        se_lat_idx = self.find_index(self.se_lat, 'latitude')
        se_lon_idx = self.find_index(self.se_lon, 'longitude')
        lat_range = slice(min(nw_lat_idx, se_lat_idx),
                          max(nw_lat_idx, se_lat_idx) + 1)
        lon_range = slice(min(nw_lon_idx, se_lon_idx),
                          max(nw_lon_idx, se_lon_idx) + 1)
        return lat_range, lon_range

    def process_data(self, starting_date=None):
        start_idx = None
        if starting_date is not None:
            time_var = self.dataset.variables['time']
            dates = num2date(
                time_var[:], units=time_var.units, calendar=time_var.calendar)
            start_date = datetime.strptime(starting_date, '%Y-%m-%d')
            if start_date < dates[0] or start_date > dates[-1]:
                raise ValueError(
                    f"Starting date {starting_date} out of dataset bounds.")
            start_idx = next(i for i, date in enumerate(
                dates) if date >= start_date)
        self.print_time_info(start_idx)
        lat_range, lon_range = self.get_lat_lon_indices()
        data = self.extract_data(lat_range, lon_range, start_idx)
        dates = self.extract_date(start_idx)
        self.save_to_csv(data, dates)


class NetCDFProcessor:
    def __init__(self, netcdf_dir, coords):
        self.netcdf_dir = netcdf_dir
        self.coords = coords

    def process_all(self, starting_date=None):
        netcdf_files = [f for f in os.listdir(
            self.netcdf_dir) if f.endswith('.nc')]
        for filename in netcdf_files:
            self.process_file(filename, starting_date)

    def process_file(self, filename, starting_date):
        filepath = os.path.join(self.netcdf_dir, filename)
        try:
            dataset = Dataset(filepath, 'r')
        except FileNotFoundError:
            print(f"File {filepath} not found. Skipping.")
            return
        variable_name = filename.split('_')[0]
        version = filename.split('_')[-1].replace('.nc', '')

        output_subdir = os.path.join('CSVClimateData', variable_name)
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
            city_extractor.process_data(starting_date=starting_date)


if __name__ == '__main__':
    coords = {
        'Istanbul': (41.3, 28.6, 40.8, 29.3),
        'Paris': (49.1, 1.8, 48.5, 3.0),
        'Madrid': (40.8, -4.0, 40.0, -3.4),
        'London': (51.7, -0.6, 51.2, 0.4),
        'Hamburg': (53.8, 9.6, 53.2, 10.5)
    }

    processor = NetCDFProcessor(netcdf_dir='netcdf4data', coords=coords)
    processor.process_all(starting_date='2013-01-01')

from datetime import datetime
from netCDF4 import Dataset, num2date
import numpy as np
import os
import json

# Change the working directory to the script's location
script_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(script_dir)

# Load configuration
with open(os.path.join(script_dir, '..', '..', 'config.json'), 'r') as config_file:
    config = json.load(config_file)


def get_data_for_day_and_coordinate(netcdf_file, target_date, target_lat, target_lon):
    # Load the NetCDF dataset
    dataset = Dataset(netcdf_file, 'r')

    # Get the time variable and convert it to dates
    time_var = dataset.variables['time']
    dates = num2date(time_var[:], units=time_var.units,
                     calendar=time_var.calendar)

    # Find the index for the target date
    target_date_obj = datetime.strptime(target_date, '%Y-%m-%d')
    date_idx = np.where(dates == target_date_obj)[0]
    if len(date_idx) == 0:
        raise ValueError(f"Date {target_date} not found in the dataset.")
    date_idx = date_idx[0]

    # Get the latitude and longitude variables
    latitudes = dataset.variables['latitude'][:]
    longitudes = dataset.variables['longitude'][:]

    # Find the index for the target latitude and longitude
    lat_idx = np.argmin(np.abs(latitudes - target_lat))
    lon_idx = np.argmin(np.abs(longitudes - target_lon))

    # Get the variable name (assuming only one variable of interest in the dataset)
    variable_name = None
    for name, var in dataset.variables.items():
        if name not in ['longitude', 'latitude', 'time']:
            variable_name = name
            break

    if variable_name is None:
        raise ValueError("No variable of interest found in the dataset.")

    # Extract the data for the specific date and coordinate
    data = dataset.variables[variable_name][date_idx, lat_idx, lon_idx]

    # Close the dataset
    dataset.close()

    return data


# Example usage
if __name__ == '__main__':
    netcdf_file = os.path.join(
        '..', '..', config['netcdf_dir'], 'tg_ens_mean_0.1deg_reg_v29.0e.nc')
    target_date = '2013-01-01'
    target_lat = 48.5
    target_lon = 2.2

    data = get_data_for_day_and_coordinate(
        netcdf_file, target_date, target_lat, target_lon)
    print(f"Data for {target_date} at ({target_lat}, {target_lon}): {data}")

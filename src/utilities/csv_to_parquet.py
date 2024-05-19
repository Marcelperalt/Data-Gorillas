import os
import pandas as pd
import json


def convert_csv_to_parquet(input_csv_file, output_parquet_file):
    """
    Converts a CSV file to Parquet format.
    """
    df = pd.read_csv(input_csv_file)
    df.to_parquet(output_parquet_file, engine='pyarrow')
    print(
        f"CSV data has been successfully converted to Parquet and saved as {output_parquet_file}")


def process_directory(directory):
    """
    Process all CSV files in the specified directory and convert them to Parquet format.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                csv_file_path = os.path.join(root, file)
                parquet_file_path = csv_file_path.replace('.csv', '.parquet')
                convert_csv_to_parquet(csv_file_path, parquet_file_path)


if __name__ == '__main__':

    # Change the working directory to the script's location
    script_dir = os.path.abspath(os.path.dirname(__file__))
    os.chdir(script_dir)

    # Load configuration
    with open(os.path.join(script_dir, '..', '..', 'config.json'), 'r') as config_file:
        config = json.load(config_file)

    # Directory containing the CSV files
    csv_directory = os.path.join('..', '..', config['csv_dir'])

    # Convert all CSV files in the directory to Parquet
    process_directory(csv_directory)

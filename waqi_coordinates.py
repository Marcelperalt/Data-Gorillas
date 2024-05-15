import requests


def get_air_quality_stations(city, token):
    # API URL for fetching city data
    url = f"https://api.waqi.info/search/?token={token}&keyword={city}"

    # Making the HTTP GET request
    response = requests.get(url)
    data = response.json()

    # Checking if the request was successful
    if data['status'] == 'ok':
        # Extracting station data
        stations = []
        for station in data['data']:
            station_name = station['station']['name']
            latitude = station['station']['geo'][0]
            longitude = station['station']['geo'][1]
            stations.append((station_name, latitude, longitude))
        return stations
    else:
        return "Failed to retrieve data"

# EXAMPLE USAGE
# List of cities
# cities = ["Paris", "Hamburg", "Istanbul", "Madrid", "London"]
# token = "42a5f642cfa03411abfb583b298be02d4ac7c23a"

# # Retrieving air quality stations for each city
# all_stations = {}
# for city in cities:
#     stations = get_air_quality_stations(city, token)
#     all_stations[city] = stations

# # Writing station data to a text file
# with open("air_quality_stations.txt", "w") as file:
#     for city, stations in all_stations.items():
#         file.write(f"City: {city}\n")
#         for station in stations:
#             file.write(
#                 f" Station Name: {station[0]}, Latitude: {station[1]}, Longitude: {station[2]}\n")
#         file.write("\n")  # Adds a blank line between cities

# print("Data has been saved to 'air_quality_stations.txt'.")

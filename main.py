import os
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime;
from dotenv import load_dotenv

load_dotenv()

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

# Configuration
BASE_URL = "https://api.openaq.org/v3"
COORDINATES = "18.808233,98.954696" # Chiang Mai University, Chiang Mai
RADIUS = 5000 # Radius size around the coordinates 5 km
TARGET_CITY = "Chiang Mai"
TARGET_COUNTRY = "TH"
TARGET_PARAMETER = 2 # 'pm2.5'
LIMITS = 1 # Limit results per request

def get_air_quality_data():
    if not OPENAQ_API_KEY:
        print("Error: OPENAQ_API_KEY not found in .env file.")
        return
    
    all_sensor_measurements = []
    sensor_locations = {}
    print(f"Fetching data from coordinates {COORDINATES} with radius {RADIUS} km for parameter {TARGET_PARAMETER}...")

    # Fetch Locations and Measurements
    try:
        url = f"{BASE_URL}/locations?coordinates={COORDINATES}&radius={RADIUS}&parameters_id={TARGET_PARAMETER}&limit={LIMITS}"
        headers = { "X-API-KEY": OPENAQ_API_KEY }
        response_locations = requests.get(url, headers=headers)
        response_locations.raise_for_status()
        response_location_data = response_locations.json()

        # Filter the JSON
        raw_locations = response_location_data.get('results', [])

        # Extracting sensors_id from the 'sensors' array within each location
        sensors_ids = []
        for location in raw_locations:
            location_id = location.get('id')
            location_name = location.get('name')
            location_country = location.get('country')
            location_city = location.get('city')
            location_coordinates = location.get('coordinates')

            for sensor in location.get('sensors', []):
                if 'id' in sensor:
                    sensor_id = sensor['id']
                    sensors_ids.append(sensor_id)
                    # Store location info with sensor_id as key
                    sensor_locations[sensor_id] = {
                        'location_id': location_id,
                        'location_name': location_name,
                        'location_country': location_country,
                        'location_city': location_city,
                        'location_latitude': location_coordinates.get('latitude') if location_coordinates else None,
                        'location_longitude': location_coordinates.get('longitude') if location_coordinates else None
                    }

        if sensors_ids:
            print("\nExtracted Sensor IDs:")
            for sensor_id in sorted(list(set(sensors_ids))): # Use set for unique, then convert to list and sort
                print(sensor_id)
        else:
            print("\nNo sensor IDs found in the response for the specified parameter.")
            return pd.DataFrame()

        for sensor_id in sensors_ids:
            print(f"\nFetching daily measurements for sensor ID: {sensor_id}")
            measure_url = f"{BASE_URL}/sensors/{sensor_id}/measurements/daily"
            try:
                response_measure = requests.get(measure_url, headers=headers)
                response_measure.raise_for_status()
                response_measure_data = response_measure.json()
                for measurement in response_measure_data.get('results', []):
                    measurement['sensor_id'] = sensor_id
                all_sensor_measurements.extend(response_measure_data.get('results', []))

                # Use for debugging if needed
                # print(f"Measurements for sensor {sensor_id}:\n")
                # print(json.dumps(response_measure_data, indent=2))

            except requests.exceptions.RequestException as e:
                print(f"Error fetching daily measurements for sensor ID {sensor_id}: {e}")
                continue

        if not all_sensor_measurements:
            print("\nNo measurements collected.")
            return pd.DataFrame()

        print(f"Converting to Pandas Dataframe...\n")

        df = pd.DataFrame(all_sensor_measurements)

        if not df.empty:
            df['date'] = df['period'].apply(lambda x: x.get('datetimeFrom', {}).get('local'))
            df['value'] = df['value']
            df['unit'] = df['parameter'].apply(lambda x: x.get('units'))
            df['parameter_name'] = df['parameter'].apply(lambda x: x.get('name'))

            columns_to_drop = [col for col in ['flagInfo', 'parameter', 'period', 'coordinates', 'summary', 'coverage'] if col in df.columns]
            df = df.drop(columns=columns_to_drop)

            df['date'] = pd.to_datetime(df['date'])

            print("\n--- Formatted Pandas DataFrame ---")
            print(df.head())
            print(f"\nDataFrame shape: {df.shape}")
            print(df.info())
        else:
            print("\nNo measurements to form a DataFrame.")

        return df

    except requests.exceptions.RequestException as e:
            print(f"Error fetching locations: {e}")
            return pd.DataFrame()

def plot_graph(df):
    if df.empty:
        print("No data to plot.")
        return

    param_name = df['parameter_name'].iloc[0] if not df.empty and 'parameter_name' in df.columns else "Unknown Parameter"
    unit_name = df['unit'].iloc[0] if not df.empty and 'unit' in df.columns else ""

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='date', y='value', hue='sensor_id', marker='o')
    plt.title(f'Daily {param_name} Levels in {TARGET_CITY} by Sensor ({unit_name})')
    plt.xlabel('Date')
    plt.ylabel(f'Concentration ({unit_name})')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    df = get_air_quality_data()
    plot_graph(df)

if __name__ == "__main__":
    main()

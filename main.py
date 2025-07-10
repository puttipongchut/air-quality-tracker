import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

# Configuration
BASE_URL = "https://api.openaq.org/v3"
COORDINATES = "13.75739,100.50662" # Center of Bangkok
RADIUS = 100 # Radius size around the coordinates
TARGET_CITY = "Bangkok"
TARGET_COUNTRY = "TH"
TARGET_PARAMETER = 2 # 'pm2.5
LIMITS = 1

def get_air_quality_data():
    if not OPENAQ_API_KEY:
        print("Error: OPENAQ_API_KEY not found in .env file.")
        return
    
    all_sensor_measurements = []
    print(f"Fetching data from coordinates {COORDINATES} with radius {RADIUS} for parameter {TARGET_PARAMETER}...")

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
            for sensor in location.get('sensors', []):
                if 'id' in sensor:
                    sensors_ids.append(sensor['id'])
        
        if sensors_ids:
            print("\nExtracted Sensor IDs:")
            for sensor_id in sorted(list(set(sensors_ids))): # Use set for unique, then convert to list and sort
                print(sensor_id)
        else:
            print("\nNo sensor IDs found in the response for the specified parameter.")

        for sensor_id in sensors_ids:
            print(f"\nFetching daily measurements for sensor ID: {sensor_id}")
            measure_url = f"{BASE_URL}/sensors/{sensor_id}/measurements/daily"
            try:
                response_measure = requests.get(measure_url, headers=headers)
                response_measure.raise_for_status()
                response_measure_data = response_measure.json()
                all_sensor_measurements.extend(response_measure_data.get('results', []))
                
                import json
                print(f"Measurements for sensor {sensor_id}:\n")
                print(json.dumps(response_measure_data, indent=2))

            except requests.exceptions.RequestException as e:
                print(f"Error fetching daily measurements for sensor ID {sensor_id}: {e}")
                continue

        print("\n--- All Collected Raw Measurements ---")
        print(json.dumps(all_sensor_measurements, indent=2))
        
        
    except requests.exceptions.RequestException as e:
            print(f"Error fetching locations: {e}")
            return

def main():
    get_air_quality_data()

if __name__ == "__main__":
    main()

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
RADIUS = "12000" # Radius size around the coordinates
TARGET_CITY = "Bangkok"
TARGET_COUNTRY = "TH"
TARGET_PARAMETER = "pm25" # Example 'pm25', 'pm10', 'o3', 'no2', 'so2', 'co'
LIMITS = 3

def get_air_quality_data():
    if not OPENAQ_API_KEY:
        print("Error: OPENAQ_API_KEY not found in .env file.")
        return

    # Fetch Data
    try:
        url = f"{BASE_URL}/locations?coordinates={COORDINATES}&radius={RADIUS}&parameter={TARGET_PARAMETER}&limit={LIMITS}"
        headers = { "X-API-KEY": OPENAQ_API_KEY }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        # Filter the JSON
        import json
        raw_measurements = response_data.get('results', [])
        print(json.dumps(raw_measurements, indent=2))
        
    except requests.exceptions.RequestException as e:
            print(f"Error fetching locations: {e}")
            return

if __name__ == "__main__":
    get_air_quality_data()

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
TARGET_PARAMETER = "pm25"
DAYS_TO_FETCH = 7

def get_air_quality_data():
    print('test')

if __name__ == "__main__":
    get_air_quality_data()

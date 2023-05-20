from dotenv import load_dotenv
import os
import googlemaps
from datetime import datetime
load_dotenv()

gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))

# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
print(geocode_result)
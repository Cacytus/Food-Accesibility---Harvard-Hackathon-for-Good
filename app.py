"""
Author: Michael Clinton
Date: 03/01/2025
"""
from flask import Flask, render_template, jsonify, request
import sqlite3
import os
import requests
import time

app = Flask(__name__)

# Database path
DB_PATH = 'instance/food.db'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/food-locations', methods=['GET', 'POST'])
def get_food_locations():
    try:
        # Connect to the existing database
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
       
        if request.method == 'POST' and request.is_json:
            # Get filter parameters from request
            filters = request.json
           
            # Start building the query
            query = "SELECT * FROM stores WHERE 1=1"
            params = []
           
            # Apply filters if provided
            if filters.get('storeName'):
                query += " AND Name LIKE ?"
                params.append(f"%{filters['storeName']}%")
           
            if filters.get('location'):
                # This would need geocoding and distance calculation
                # For simplicity, we're just doing a text search on address
                query += " AND Address LIKE ?"
                params.append(f"%{filters['location']}%")
           
            if filters.get('priceRange'):
                query += " AND price_range = ?"
                params.append(filters['priceRange'])
           
            if filters.get('ethnicFoodType') and filters['ethnicFoodType'] != "Any":
                query += " AND Ethnicity = ?"
                params.append(filters['ethnicFoodType'])
           
            if filters.get('snap'):
                query += " AND EBT = 'yes'"
           
            # Execute the filtered query
            cursor.execute(query, params)
        else:
            # If no filters provided, return all stores
            cursor.execute("SELECT * FROM stores")
       
        rows = cursor.fetchall()
       
        # Convert to list of dicts
        locations = []
        for row in rows:
            try:
                # Get coordinates for the address
                lat, lng = geocode_address(row['Address'])
                
                # Determine price range (using a placeholder since it's not in your DB)
                price_range = "$" # Default value
                
                locations.append({
                    "name": row['Name'],
                    "address": row['Address'],
                    "website": row['URL'],
                    "price_range": price_range,
                    "lat": lat,
                    "lng": lng,
                    "snap_accepted": row['EBT'].lower() == 'yes',
                    "ethnic_food_type": row['Ethnicity']
                })
                # Add a small delay to avoid overwhelming geocoding service
                time.sleep(0.1)
            except Exception as e:
                print(f"Error processing row {row['Name']}: {e}")
       
        conn.close()
        return jsonify(locations)
   
    except Exception as e:
        print(f"Error accessing database: {e}")
        return jsonify({"error": str(e)}), 500

def geocode_address(address):
    """
    Convert an address to latitude and longitude using OpenStreetMap's Nominatim service.
    """
    try:
        # Use Nominatim for geocoding (respect usage policy with delay)
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "FoodStoreLocatorApp/1.0"  # Specify a user agent as required by Nominatim
        }
        
        response = requests.get(nominatim_url, params=params, headers=headers)
        data = response.json()
        
        if data and len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            # Default to Boston coordinates if geocoding fails
            print(f"Could not geocode address: {address}")
            return 42.3601, -71.0589
    except Exception as e:
        print(f"Geocoding error: {e}")
        # Default to Boston coordinates
        return 42.3601, -71.0589

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Warning: {DB_PATH} does not exist. Please create it with the required schema.")
    app.run(debug=True)
"""
Author: Michael Clinton
Date: 03/01/2025
"""
from flask import Flask, render_template, jsonify, request
import sqlite3
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

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
                # Filter by location text
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
                # Get coordinates from the database
                lat = row['Lat']
                lng = row['Long']
                
                # Clean up potential string values (in case they're stored that way)
                if lat and isinstance(lat, str):
                    lat = lat.strip()
                if lng and isinstance(lng, str):
                    lng = lng.strip()
                
                # Skip entries without valid coordinates
                if not lat or not lng:
                    continue
                
                # Try to convert to float (will raise ValueError if not convertible)
                try:
                    lat = float(lat)
                    lng = float(lng)
                except (ValueError, TypeError):
                    print(f"Invalid coordinates for {row['Name']}: Lat={lat}, Long={lng}")
                    continue
                
                # Skip entries with zero coordinates (likely placeholders)
                if lat == 0 or lng == 0:
                    print(f"Zero coordinates for {row['Name']}")
                    continue
                
                # Create the location dict for this store
                locations.append({
                    "name": row['Name'],
                    "address": row['Address'],
                    "website": row['URL'],
                    "price_range": "$", # Default value since not in DB
                    "lat": lat,
                    "lng": lng,
                    "snap_accepted": row['EBT'].lower() == 'yes' if row['EBT'] else False,
                    "ethnic_food_type": row['Ethnicity']
                })
            except Exception as e:
                print(f"Error processing row {row['Name'] if 'Name' in row else 'unknown'}: {e}")
       
        conn.close()
        
        if not locations:
            print("Warning: No locations found with valid coordinates")
            
        return jsonify(locations)
   
    except Exception as e:
        print(f"Error accessing database: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Warning: {DB_PATH} does not exist. Please create it with the required schema.")
    app.run(debug=True)
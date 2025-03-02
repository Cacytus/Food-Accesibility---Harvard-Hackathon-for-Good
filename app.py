"""
Author: Michael Clinton
Date: 03/01/2025
"""
from flask import Flask, render_template, jsonify, request
import sqlite3
import os

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
                query += " AND name LIKE ?"
                params.append(f"%{filters['storeName']}%")
            
            if filters.get('location'):
                # This would need geocoding and distance calculation
                # For simplicity, we're just doing a text search on address
                query += " AND address LIKE ?"
                params.append(f"%{filters['location']}%")
            
            if filters.get('priceRange'):
                query += " AND price_range = ?"
                params.append(filters['priceRange'])
            
            if filters.get('ethnicFoodType') and filters['ethnicFoodType'] != "Any":
                query += " AND ethnic_food_type = ?"
                params.append(filters['ethnicFoodType'])
            
            if filters.get('snap'):
                query += " AND snap_accepted = 1"
            
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
                locations.append({
                    "id": row['id'],
                    "name": row['name'],
                    "address": row['address'],
                    "website": row['website'],
                    "price_range": row['price_range'],
                    "lat": row['lat'],
                    "lng": row['lng'],
                    "snap_accepted": bool(row['snap_accepted']),
                    "ethnic_food_type": row['ethnic_food_type']
                })
            except Exception as e:
                print(f"Error processing row: {e}")
        
        conn.close()
        return jsonify(locations)
    
    except Exception as e:
        print(f"Error accessing database: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Warning: {DB_PATH} does not exist. Please create it with the required schema.")
    app.run(debug=True)
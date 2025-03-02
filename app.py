"""
Author: LucyM
Date: 03/01/2025
"""
from flask import Flask, render_template, jsonify, request
import sqlite3
import os
import requests
import json
import time

app = Flask(__name__)

# Database setup
DB_PATH = 'food_access.db'

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create stores table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        price_range TEXT,
        lat REAL,
        lng REAL,
        snap_accepted INTEGER DEFAULT 0,
        food_type TEXT
    )
    ''')
    
    # Check if we need to populate sample data
    cursor.execute("SELECT COUNT(*) FROM stores")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Sample data for Boston area
        sample_stores = [
            ("Trader Joe's", "899 Boylston St, Boston, MA 02115", "$$", 1, "grocery"),
            ("Whole Foods Market", "181 Cambridge St, Boston, MA 02114", "$$$", 1, "grocery"),
            ("Star Market", "1275 Boylston St, Boston, MA 02215", "$$", 1, "grocery"),
            ("Boston Public Market", "100 Hanover St, Boston, MA 02108", "$$", 0, "market"),
            ("Haymarket", "Blackstone St, Boston, MA 02109", "$", 1, "market"),
            ("Stop & Shop", "60 Everett St, Allston, MA 02134", "$", 1, "grocery"),
            ("H Mart", "581 Massachusetts Ave, Cambridge, MA 02139", "$$", 0, "asian"),
            ("Foodie's Market", "1421 Washington St, Boston, MA 02118", "$$", 0, "grocery"),
            ("Daily Table", "450 Washington St, Dorchester, MA 02124", "$", 1, "grocery"),
            ("Market Basket", "400 Somerville Ave, Somerville, MA 02143", "$", 1, "grocery")
        ]
        
        # Get coordinates for each store using Nominatim
        for store in sample_stores:
            name, address, price, snap, food_type = store
            lat, lng = get_coordinates(address)
            
            # Insert with coordinates
            cursor.execute(
                "INSERT INTO stores (name, address, price_range, lat, lng, snap_accepted, food_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, address, price, lat, lng, snap, food_type)
            )
            # Sleep to respect Nominatim usage policy
            time.sleep(1)
    
    conn.commit()
    conn.close()

def get_coordinates(address):
    """Get latitude and longitude for an address using Nominatim"""
    # Add Boston, MA to make sure we get results in Boston area
    if "Boston" not in address and "MA" not in address:
        address += ", Boston, MA"
    
    # Format address for URL
    formatted_address = address.replace(' ', '+')
    
    # Nominatim API request (with proper user agent as required by their usage policy)
    url = f"https://nominatim.openstreetmap.org/search?q={formatted_address}&format=json&limit=1"
    headers = {"User-Agent": "BostonFoodAccessMap/1.0"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data and len(data) > 0:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            # Default to Boston Common if address not found
            print(f"Could not find coordinates for: {address}")
            return 42.3551, -71.0656
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        # Default to Boston Common
        return 42.3551, -71.0656

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/food-locations', methods=['GET', 'POST'])
def get_food_locations():
    if request.method == 'POST':
        # Get filter parameters from request
        filters = request.json
        # Build query based on filters (to be implemented)
    
    # For now, just return all locations
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM stores")
    rows = cursor.fetchall()
    
    # Convert to list of dicts
    locations = []
    for row in rows:
        locations.append({
            "id": row['id'],
            "name": row['name'],
            "address": row['address'],
            "price_range": row['price_range'],
            "lat": row['lat'],
            "lng": row['lng'],
            "snap_accepted": bool(row['snap_accepted']),
            "food_type": row['food_type']
        })
    
    conn.close()
    return jsonify(locations)

if __name__ == '__main__':
    # Initialize database before starting app
    init_db()
    app.run(debug=True)
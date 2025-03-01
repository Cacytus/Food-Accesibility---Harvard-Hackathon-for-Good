"""
Author: LucyM
Date: 03/01/2025
"""
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    # Placeholder: pass an empty list or sample data as needed
    return render_template('index.html')

# API endpoint for getting filtered food locations (to be implemented later)
@app.route('/api/food-locations', methods=['POST'])
def get_food_locations():
    # Get filter parameters from request
    filters = request.json
    
    # Placeholder: In the future, you'll query your database based on filters
    # and return matching food locations
    
    # Sample response format
    sample_locations = [
        {
            "id": 1,
            "name": "Sample Food Store",
            "lat": 42.3601,
            "lng": -71.0589,
            "type": "grocery",
            "price": "$",
            "snap": True
        }
    ]
    
    return jsonify(sample_locations)

if __name__ == '__main__':
    app.run(debug=True)
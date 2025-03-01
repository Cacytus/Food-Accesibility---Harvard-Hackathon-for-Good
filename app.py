"""
Author: LucyM
Date: 03/01/2025
"""
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    # Placeholder: pass an empty list or sample data as needed
    stores = []
    return render_template('index.html', stores=stores)

if __name__ == '__main__':
    app.run(debug=True)

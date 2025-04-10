"""
Web Application for Microphone Translation.

This Flask app connects to a MongoDB database and handles routes
 to interact with the microphone translation app.
"""

import os
import datetime
from flask import Flask, render_template, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)


@app.route("/")
def home():
    """Home page for the web app."""
    return render_template('index.html')


@app.route("/translator")
def translator():
    """ translate page """
    return render_template('translator.html')

@app.route("/register")
def register():
    """ Sign in page"""
    #when user authenticated 
    #redirect to login page 
    return render_template('register.html')

@app.route("/login")
def login():
    """Login page"""
    #when user authenticated 
    #redirect to translate page
    return render_template('login.html')

@app.route("/logout", methods=["POST"])
def logout():
    """Logout Functionality"""
    #logout user with flask login 
    return redirect(url_for("home"))

@app.route("/api/sensor_data", methods=["GET"])
def get_sensor_data():
    """Get sensor data from MongoDB."""
    sensor_data = list(mongo.db.sensor_data.find({}))
    for record in sensor_data:
        record["_id"] = str(record["_id"])
        if "timestamp" in record:
            record["timestamp"] = record["timestamp"].isoformat()
    return jsonify(sensor_data)

@app.route("/simulate_input", methods=["GET"])
def simulate_input():
    test_document = {
        "input_text": "Hello, world! How are you?",
        "target_language": "es",
        "timestamp": datetime.datetime.now()
    }
    result = mongo.db.sensor_data.insert_one(test_document)
    return jsonify({
        "message": "Test document inserted",
        "id": str(result.inserted_id)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

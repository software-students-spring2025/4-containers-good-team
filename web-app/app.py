"""
Web Application for Microphone Translation.

This Flask app connects to a MongoDB database and handles routes
 to interact with the microphone translation app.
"""

import os
import datetime
from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)


@app.route("/")
def home():
    """Home page for the web app."""
    return render_template("index.html")


@app.route("/translator")
def translator():
    """translate page"""
    return render_template("translator.html")

@app.route("/account")
def account():
    """Logout Functionality"""
    # logout user with flask login
    return render_template("account.html")


@app.route("/register")
def register():
    """Sign in page"""
    # when user authenticated
    # redirect to login page
    return render_template("register.html")


@app.route("/login")
def login():
    """Login page"""
    # when user authenticated
    # redirect to translate page
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    """Logout Functionality"""
    # logout user with flask login
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
    """Simulate a test document in MongoDB."""
    test_document = {
        "input_text": "Hello, world! How are you?",
        "target_language": "es",
        "timestamp": datetime.datetime.now(),
    }
    result = mongo.db.sensor_data.insert_one(test_document)
    return jsonify({"message": "Test document inserted", "id": str(result.inserted_id)})


@app.route("/submit_text", methods=["POST"])
def submit_text():
    """Backend function to receive user-submitted text (from microphone)"""
    data = request.get_json()
    input_text = data.get("input_text")
    target_language = data.get("target_language", "es")
    if not input_text:
        return jsonify({"error": "Input text is required"}), 400
    document = {
        "input_text": input_text,
        "target_language": target_language,
        "timestamp": datetime.datetime.now(),
    }
    result = mongo.db.sensor_data.insert_one(document)
    return jsonify(
        {"message": "Text submitted successfully", "id": str(result.inserted_id)}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

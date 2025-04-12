"""
Web Application for Microphone Translation.

This Flask app connects to a MongoDB database and handles routes
 to interact with the microphone translation app.
"""

import os
import datetime
from flask import (Flask, render_template, redirect, url_for, jsonify, request, session, flash)
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback_key_if_missing")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# defining collections
users_collection = mongo.db.users       # registration
sensor_data_collection = mongo.db.sensor_data  # sensor data and translations


@app.route("/")
def home():
    """First page for the web app."""
    return render_template("login.html")

@app.route("/home")
def index():
    """First page for logged in users that shows quick links and recent translations."""
    if not session.get("username"):
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for("login"))
    recent_translations = list(
        mongo.db.sensor_data.find({}).sort("timestamp", -1).limit(10)
    )
    for record in recent_translations:
        record["_id"] = str(record["_id"])
        if "timestamp" in record:
            record["timestamp"] = record["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return render_template('index.html', recent_translations=recent_translations)


@app.route("/translator")
def translator():
    """Translate page"""
    # check if logged
    if not session.get("username"):
        flash("You must be logged in to access the translator.", "warning")
        return redirect(url_for("login"))
    return render_template('translator.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Sign in page"""
    # authenticate user
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if not (first_name and last_name and email and password and confirm_password):
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))
        # check if  user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("User already exists with that email.", "danger")
            return redirect(url_for("register"))
        # create a new user
        new_user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": generate_password_hash(password),
            "created_at": datetime.datetime.utcnow()
        }
        users_collection.insert_one(new_user)
        user = users_collection.find_one({"email": email})
        session["user_id"] = str(user["_id"])
        session["username"] = user["email"]
        flash("Registration successful! You can now log in.", "success")
        # redirect to login page
        return redirect(url_for("index"))
    # get request; render registration form
    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    #when user authenticated
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # Check for a user with the provided email
        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = user["email"]
            flash("Logged in successfully!", "success")
            #redirect to translate page
            return redirect(url_for("translator"))
        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))
    # get request; render login page
    return render_template('login.html')

@app.route("/logout", methods=["GET"])
def logout():
    """Logout Functionality"""
    session.clear()
    flash("Logged out successfully.", "success")
    #logout user with flask login
    return redirect(url_for("home"))

@app.route("/account")
def account():
    """User account page that shows past translations."""
    if not session.get("username"):
        flash("You must be logged in to view your account.", "warning")
        return redirect(url_for("login"))
    # Fetch this user's translations by filtering with session["user_id"]
    user = users_collection.find_one({"_id": ObjectId(session.get("user_id"))})
    user_translations = list(
        sensor_data_collection.find({"user_id": session.get("user_id")}).sort("timestamp", -1)
    )
    for record in user_translations:
        record["_id"] = str(record["_id"])
        if "timestamp" in record:
            record["timestamp"] = record["timestamp"].isoformat()
        if "translated_timestamp" in record:
            record["translated_timestamp"] = record["translated_timestamp"].isoformat()
    return render_template("account.html", user=user, translations=user_translations)


# Endpoints for sensor/translation data
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
    # Build the document and include a user identifier if logged in
    document = {
        "input_text": input_text,
        "target_language": target_language,
        "timestamp": datetime.datetime.now(),
    }
    if session.get("user_id"):
        document["user_id"] = session.get("user_id")
    if session.get("username"):
        document["translator"] = session.get("username")
    result = mongo.db.sensor_data.insert_one(document)
    return jsonify({
        "message": "Text submitted successfully",
        "id": str(result.inserted_id)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

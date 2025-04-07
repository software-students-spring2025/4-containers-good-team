"""
Web Application for Microphone Translation.

This Flask app connects to a MongoDB database and handles routes 
to interact with the microphone translation app.
"""
import os
from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

@app.route("/")
def home():
    """Home page for the web app."""
    return "<h1>hello<h1>"

if __name__ == "__main__":
    """Start the web app."""
    app.run(host="0.0.0.0", port=5050)

"""
Web Application for Microphone Translation.

This Flask app connects to a MongoDB database and handles routes
 to interact with the microphone translation app.
"""

import os
from flask import Flask, render_template, redirect, url_for
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

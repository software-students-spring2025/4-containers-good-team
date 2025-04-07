from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

@app.route("/")
def home():
    return "<h1>hello<h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
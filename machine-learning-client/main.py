"""
Machine Learning Client for MongoDB Integration.

This script connects to a MongoDB database using the connection string.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    raise ValueError("MONGO_URI not set in .env")

client = MongoClient(mongo_uri)
db = client.get_default_database()

print(f"Connected to MongoDB at {mongo_uri}")
print("Machine learning client is running.")

"""
Machine Learning Client for MongoDB Integration.

This script connects to a MongoDB database using the connection string.
"""

import os
import time
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from googletrans import Translator

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI not set in .env")

client = MongoClient(mongo_uri)
db = client.get_default_database()

translator = Translator()

def process_untranslated_records():
    pending_records = list(db.sensor_data.find({
        "input_text": {"$exists": True}, 
        "translated_text": {"$exists": False}
    }))

    if pending_records:
        print(f"Processing {len(pending_records)} records...")
        for record in pending_records:
            raw_text = record["input_text"]
            target_language = record.get("target_language", "es")
            try:
                result = translator.translate(raw_text, dest=target_language)
                translated_text = result.text
                
                db.sensor_data.update_one(
                    {"_id": record["_id"]},
                    {"$set": {
                        "translated_text": translated_text,
                        "translated_timestamp": datetime.datetime.now()
                        }}
                )
                print(f"Traslated '{raw_text}' to '{translated_text}' for record {record['_id']}")
            except Exception as e:
                print(f"Error translating record {record['_id']}: {e}")
    else:
        print("No new translation jobs found.")

if __name__ == "__main__":
    print("Translation ML Client is running. Press Ctrl+C to exit.")
    try:
        while True:
            process_untranslated_records()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Translation ML Client stopped.")
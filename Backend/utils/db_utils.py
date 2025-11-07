# Backend/utils/db_utils.py
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client['SecurityAlerts']
collection = db['Detections']

def save_alert_to_db(alert_type,
                     location="Camera 1",
                     confidence=None,
                     people_count=None,
                     sub_type=None,
                     person_name=None,
                     violence_detected=False):
    """
    Save a detection record to MongoDB.

    - alert_type: string or list (e.g. "Weapon" or ["Weapon","Crowd"])
    - sub_type: e.g. "gun", "knife", etc.
    - person_name: e.g. recognized person (for criminal detection)
    - violence_detected: boolean
    """
    now = datetime.now()

    # Keep "type" as an array for easier analytics
    if isinstance(alert_type, list):
        types = alert_type
    else:
        types = [alert_type] if alert_type is not None else []

    document = {
        "type": types,
        "sub_type": sub_type,
        "person_name": person_name,
        "confidence": confidence,
        "people_count": people_count,
        "violence_detected": bool(violence_detected),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "location": location
    }

    try:
        collection.insert_one(document)
    except Exception as e:
        # fail silently but print to logs for debugging
        print(f"[db_utils] Failed to insert document: {e}")
        print(document)

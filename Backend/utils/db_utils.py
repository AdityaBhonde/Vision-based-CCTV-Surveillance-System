# Backend/utils/db_utils.py
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# IMPORT TELEGRAM
from utils.telegram_utils import send_telegram_alert


# ------------- MONGO CONNECTION -------------
client = MongoClient("mongodb://localhost:27017/")
db = client["SecurityAlerts"]
collection = db["Detections"]


# =====================================================
# 🔥 Recommendation Helper
# =====================================================
def recommendation_text(alert_type, sub_type=None):
    alert_type = (alert_type or "").lower()

    if "weapon" in alert_type:
        return "Possible weapon detected. Send nearest guard immediately."

    if "criminal" in alert_type:
        return "Criminal face match detected. Verify CCTV and alert authorities."

    if "violence" in alert_type:
        return "Suspicious violence detected. Take urgent action."

    if "crowd" in alert_type:
        return "Crowd increasing. Monitor area for unusual activity."

    return "Please monitor the area."


# =====================================================
# 🔥 Save alert + Telegram notifier
# =====================================================
def save_alert_to_db(
    alert_type: str,
    sub_type: Optional[str] = None,
    person_name: Optional[str] = None,
    confidence: Optional[float] = None,
    people_count: Optional[int] = None,
    location: str = "Camera 1",
    violence_detected: bool = False,
    frame=None
) -> None:

    # ========== WEAPON CONFIDENCE RULE ==========
    if alert_type and alert_type.lower() == "weapon":
        if confidence is None or float(confidence) < 0.50:
            print(f"[DB] Weapon ignored (< 50% conf): {confidence}")
            return

    # ========== SAVE INTO MONGO ==========
    now = datetime.now()
    doc = {
        "type": [alert_type],
        "sub_type": sub_type,
        "person_name": person_name,
        "confidence": float(confidence) if confidence else None,
        "people_count": int(people_count) if people_count else 0,
        "violence_detected": bool(violence_detected),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "location": location,
    }

    collection.insert_one(doc)
    print("[DB] Alert Saved:", doc)

    # ========== BUILD TELEGRAM MESSAGE ==========
    readable_conf = f"{round(confidence * 100)}%" if confidence else "N/A"
    violence_text = "Yes" if violence_detected else "No"

    msg = f"""
🚨 *SECURITY ALERT DETECTED*  

• *Type:* {alert_type}  
• *Subtype:* {sub_type or "-"}  
• *Criminal:* {person_name or "-"}  
• *Confidence:* {readable_conf}  
• *People Count:* {people_count or 0}  
• *Violence:* {violence_text}  
• *Location:* {location}  
• *Time:* {now.strftime("%d-%b-%Y %H:%M:%S")}  

⚠️ *Risk Level:* {"HIGH" if confidence and confidence >= 0.75 else "MODERATE"}  

🔍 *Recommended Action:*  
{recommendation_text(alert_type, sub_type)}
"""

    # ========== SEND TELEGRAM ALERT ==========
    try:
        send_telegram_alert(msg, frame)
    except Exception as e:
        print("[TELEGRAM ERROR]", e)


# =====================================================
# ANALYTICS HELPERS (unchanged)
# =====================================================
def total_alerts_today() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    return collection.count_documents({"date": today})


def unique_criminals_today() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    return len(
        collection.distinct(
            "person_name",
            {"date": today, "person_name": {"$ne": None}}
        )
    )


def alerts_last_n_days(days: int = 7) -> List[Dict[str, Any]]:
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return list(collection.find({"date": {"$gte": since}}))


def aggregate_type_counts(days: int = 7) -> List[Dict[str, Any]]:
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    pipeline = [
        {"$match": {"date": {"$gte": since}}},
        {"$unwind": {"path": "$type"}},
        {"$group": {"_id": "$type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return list(collection.aggregate(pipeline))


def aggregate_top_subtypes(limit: int = 8) -> List[Dict[str, Any]]:
    pipeline = [
        {"$match": {"sub_type": {"$ne": None}}},
        {"$group": {"_id": "$sub_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    return list(collection.aggregate(pipeline))


def crowd_trend(days: int = 7) -> List[Dict[str, Any]]:
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    pipeline = [
        {"$match": {"date": {"$gte": since}}},
        {
            "$group": {
                "_id": "$date",
                "avg_people": {"$avg": {"$ifNull": ["$people_count", 0]}},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    return [
        {"date": doc["_id"], "avg_people": round(doc.get("avg_people", 0), 2)}
        for doc in collection.aggregate(pipeline)
    ]


def hourly_counts_today() -> List[Dict[str, Any]]:
    today = datetime.now().strftime("%Y-%m-%d")
    pipeline = [
        {"$match": {"date": today}},
        {"$group": {"_id": {"$substr": ["$time", 0, 2]}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    return [{"hour": doc["_id"], "count": doc["count"]} for doc in collection.aggregate(pipeline)]


def recent_alerts(limit: int = 50) -> List[Dict[str, Any]]:
    return list(collection.find().sort([("_id", -1)]).limit(limit))


def predict_peak_hour() -> str:
    hourly = hourly_counts_today()
    if not hourly:
        return "No activity"

    top = max(hourly, key=lambda x: x["count"])
    hour = int(top["hour"])
    return f"{hour:02d}:00 - {hour:02d}:59"


def most_active_location() -> str:
    pipeline = [
        {"$group": {"_id": "$location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1},
    ]
    docs = list(collection.aggregate(pipeline))
    return docs[0]["_id"] if docs else "N/A"


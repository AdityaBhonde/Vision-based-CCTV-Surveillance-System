from flask import Blueprint, jsonify
from utils.db_utils import recent_alerts
from bson import ObjectId   # <-- IMPORTANT

alerts_bp = Blueprint("alerts", __name__)

def serialize_alert(alert):
    alert["_id"] = str(alert["_id"])   # Convert ObjectId → string
    return alert

@alerts_bp.route("/alerts/recent")
def recent_alerts_list():
    alerts = recent_alerts(40)
    alerts = [serialize_alert(a) for a in alerts]  # Convert all
    return jsonify(alerts)


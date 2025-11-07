from flask import Blueprint, jsonify
from utils.db_utils import collection

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/api/alerts', methods=['GET'])
def get_alerts_log():
    try:
        alerts_cursor = collection.find({}).sort('date', -1).limit(100)
        alerts_list = []
        for alert in alerts_cursor:
            alert['_id'] = str(alert['_id'])
            alerts_list.append(alert)
        return jsonify(alerts_list)
    except Exception as e:
        print(f"Error retrieving alert log: {e}")
        return jsonify({"error": "Failed to retrieve alert log"}), 500

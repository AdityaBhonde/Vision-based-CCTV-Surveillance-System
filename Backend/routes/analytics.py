from flask import Blueprint, jsonify
from utils.db_utils import collection
from datetime import datetime, timedelta
from collections import Counter

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    since = datetime.now() - timedelta(days=1)
    alerts = list(collection.find({}))
    filtered_alerts = []

    for alert in alerts:
        try:
            alert_datetime_str = f"{alert['date']} {alert['time']}"
            alert_datetime = datetime.strptime(alert_datetime_str, '%Y-%m-%d %H:%M:%S')
            if alert_datetime >= since:
                filtered_alerts.append(alert)
        except (KeyError, ValueError):
            continue

    alert_types = [alert['type'] for alert in filtered_alerts]
    type_counts = Counter(alert_types)

    for t in ['Crowd', 'Weapon', 'Violence']:
        if t not in type_counts:
            type_counts[t] = 0

    return jsonify(type_counts)

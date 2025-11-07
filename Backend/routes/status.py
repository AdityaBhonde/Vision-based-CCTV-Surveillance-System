from flask import Blueprint, jsonify
import shared_state as state
import time

status_bp = Blueprint('status', __name__)

@status_bp.route('/get_status')
def get_status():
    now = time.time()
    with state.status_lock:
        weapon_status = state.last_weapon_info if (state.last_weapon_detection_time and now - state.last_weapon_detection_time <= state.ALERT_COOLDOWN) else "Safe"
        violence_status = state.last_violence_info if (state.last_violence_detection_time and now - state.last_violence_detection_time <= state.ALERT_COOLDOWN) else "Safe"
    
    return jsonify({
        "crowd_count": state.crowd_count,
        "weapon_status": weapon_status,
        "violence_status": violence_status,
        "system_active": state.detection_active
    })

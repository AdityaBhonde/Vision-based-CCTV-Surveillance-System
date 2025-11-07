import threading

# --- THREAD LOCKS ---
frame_lock = threading.Lock()
status_lock = threading.Lock()

# --- DETECTION STATUS ---
processed_frames = {'crowd': None, 'weapon': None, 'violence': None}
detection_active = False

# --- MODELS ---
yolo_crowd_model = None
yolo_weapon_model = None
violence_model = None
camera_manager = None

# --- TRACKING DATA ---
crowd_count = "0"
crowd_history = []
last_weapon_detection_time = None
last_weapon_info = "Safe"
last_violence_detection_time = None
last_violence_info = "Safe"

# --- CONSTANTS ---
ALERT_COOLDOWN = 12
DETECTION_CONF_THRESHOLD = 0.20

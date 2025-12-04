
---

# 🛡️ **AI-Powered Smart Security Surveillance System**

### *Weapon Detection • Criminal Recognition • Crowd Analysis • Real-Time Alerts • Telegram Monitoring • Analytics Dashboard*

---

## 📌 **Overview**

This project is a **complete AI-driven surveillance platform** designed for real-time threat detection.
It integrates **YOLO-based weapon detection, criminal face recognition, crowd analysis, violence detection, MongoDB analytics**, and a full-fledged **React dashboard** with PDF reporting and Telegram alerts.

The system is designed for:

* College campus monitoring
* Malls & public areas
* Smart city surveillance
* Security control rooms
* Automated guard-alert systems

---

## 🚨 **Core Features**

### **1️⃣ Real-Time AI Detection**

| Detection Type                    | Description                                                |
| --------------------------------- | ---------------------------------------------------------- |
| 🔫 **Weapon Detection**           | Detects guns/knives using YOLO with >50% confidence filter |
| 🧑‍🤝‍🧑 **Crowd Analysis**       | Counts people, detects crowd density, triggers warnings    |
| 🧟‍♂️ **Criminal Identification** | Face recognition using pre-encoded known faces             |
| ⚔️ **Violence Detection**         | Detects fights/suspicious actions                          |
| 📍 **Location Tagging**           | Automatically maps every alert to the camera source        |

---

### **2️⃣ Alert Automation**

* Alerts saved instantly to **MongoDB**
* Telegram bot sends **emergency notifications**
* Includes:

  * Threat level
  * Confidence score
  * Detected person (if criminal)
  * Location & timestamp
  * Recommended action
  * Optional CCTV frame photo

---

### **3️⃣ Advanced Analytics Dashboard (React + Vite + Tailwind)**

The dashboard displays:

#### 📊 **Summary Cards**

* Total Alerts Today
* Criminals Detected
* Active Cameras
* Safety Index

#### 📈 **Charts**

* Alerts by category (7 days)
* Hourly alerts trend
* Crowd density heatmap
* Person reappearance tracker

#### 🔊 **AI Voice Assistant**

* Generates **English** and **Hinglish** spoken summaries
* Helps security guards understand the situation quickly

#### 📄 **PDF Reporting**

Exports a full-day surveillance report including:

* Graphs
* Alerts
* Trends
* Highlights
* Recommendations

---

### **4️⃣ Modular Backend Architecture**

* Flask server
* Optimized threaded camera pipeline
* Modular detection scripts
* Analytics blueprint
* Telegram & database utilities

---

## 🗂️ **Project Structure**

```
📦 Backend
│── app.py
│── shared_state.py
│── report_generator.py
│── detection/
│   ├── crowd.py
│   ├── weapon.py
│   ├── criminal.py
│── routes/
│   ├── alerts.py
│   ├── analytics.py
│   ├── status.py
│── utils/
│   ├── db_utils.py
│   ├── telegram_utils.py
│── models/
│   ├── CrowdDetection/best.pt
│   ├── Weapon_Detection/weapon.pt
│   ├── Criminal/encodings.pickle
│
📦 Frontend
│── src/
│   ├── pages/AnalyticsDashboard.tsx
│   ├── components/
│── public/
│── package.json
```

---

# ⚙️ **Technology Stack**

### **Backend**

* Python 3.11
* Flask
* OpenCV
* Ultranytics YOLO
* MongoDB
* Face Recognition
* ReportLab (PDF generator)
* Telegram Bot API

### **Frontend**

* React + TypeScript
* Vite
* TailwindCSS
* ShadCN UI
* Recharts
* Lucide Icons

---

# 🛠️ **Installation Guide**

---

## **1️⃣ Backend Setup**

### **Install dependencies**

```sh
pip install flask flask-cors pymongo ultralytics opencv-python reportlab python-telegram-bot==13.15
```

### **Run backend**

```sh
py app.py
```

Backend starts at:

```
http://127.0.0.1:5000
```

---

## **2️⃣ Frontend Setup**

### Install dependencies

```sh
npm install
```

### Start frontend

```sh
npm run dev
```

Frontend runs at:

```
http://localhost:8080
```

---

# 🔗 **Key API Endpoints**

| Method | Endpoint                     | Description                       |
| ------ | ---------------------------- | --------------------------------- |
| GET    | `/analytics/summary`         | Summary cards data                |
| GET    | `/analytics/trends`          | Graphs & charts data              |
| GET    | `/alerts/recent`             | Last 50 alerts                    |
| GET    | `/analytics/generate_report` | PDF report download               |
| POST   | `/api/start_detection`       | Starts camera + detection threads |

---

# 📲 **Telegram Alerts**

Each alert message contains:

```
🚨 SECURITY ALERT DETECTED  

• Type: Weapon  
• Subtype: Gun  
• Criminal: None  
• Confidence: 94%  
• People Count: 3  
• Violence: No  
• Location: Camera 1  
• Time: 04-Dec-2025 15:22:10  

⚠️ Risk Level: HIGH  

🔍 Recommended Action:
Possible weapon detected. Send nearest guard immediately.
```

👉 Photos can also be sent if frame capturing is enabled.

---

# 📄 **PDF Report Generation**

Exports a high-quality PDF containing:

* Daily alert summary
* Graphs
* Hourly trends
* High-risk zones
* Observations
* Suggestions

Called from frontend:

```ts
fetch("http://127.0.0.1:5000/analytics/generate_report");
```

---

# 🔮 **Future Enhancements**

* Multi-camera distributed server
* GPS mapping for cameras
* Audio gunshot detection
* LSTM threat prediction model
* WebSocket real-time updates
* Face re-identification engine

---

# 🙌 **Acknowledgements**

This project uses:

* YOLO by Ultralytics
* ReportLab
* python-telegram-bot
* MongoDB
* React + Tailwind
* ShadCN UI

---

# 🎯 **Final Notes**

This is a **production-ready surveillance system**, capable of being deployed in:

✔ Campuses
✔ Offices
✔ Public spaces
✔ Security control rooms

---


# ===================== routes/analytics.py (FINAL CLEAN VERSION) =====================
from flask import Blueprint, jsonify, request, send_file, current_app
from datetime import datetime
from bson import ObjectId
import os
import traceback

# DB utilities
from utils.db_utils import (
    total_alerts_today,
    unique_criminals_today,
    aggregate_type_counts,
    aggregate_top_subtypes,
    crowd_trend,
    hourly_counts_today,
    predict_peak_hour,
    most_active_location,
    recent_alerts,
    collection
)

# Import PDF generator
try:
    from report_generator import build_daily_pdf
except Exception as e:
    print("PDF Import FAILED:", e)
    build_daily_pdf = None

analytics_bp = Blueprint("analytics", __name__)


# ---------------------- Helper ----------------------
def safe_doc(doc):
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        else:
            out[k] = v
    return out


# ---------------------- SUMMARY API ----------------------
@analytics_bp.route("/analytics/summary", methods=["GET"])
def analytics_summary():
    try:
        total_alerts = total_alerts_today()
        criminals = unique_criminals_today()

        safety_index = max(0, 100 - (total_alerts * 3))

        return jsonify({
            "total_alerts_today": total_alerts,
            "detected_criminals": criminals,
            "active_cameras": 1,
            "safety_index": safety_index,
            "peak_hour": predict_peak_hour(),
            "top_location": most_active_location(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------- TRENDS API ----------------------
@analytics_bp.route("/analytics/trends", methods=["GET"])
def analytics_trends():
    try:
        return jsonify({
            "by_type": aggregate_type_counts(7),
            "crowd_trend": crowd_trend(7),
            "hourly_today": hourly_counts_today(),
            "top_subtypes": aggregate_top_subtypes(8),
        })
    except Exception as e:
        current_app.logger.error("TREND ERROR: %s", e)
        return jsonify({"error": "trend failure"}), 500


# ---------------------- RECENT ALERTS API ----------------------
@analytics_bp.route("/alerts/recent", methods=["GET"])
def analytics_recent_alerts():
    try:
        limit = int(request.args.get("limit", 40))
        raw = recent_alerts(limit)

        out = []
        for r in raw:
            types = r.get("type") or []
            conf = r.get("confidence")

            # ------------- Filter: Weapon confidence < 50% ----------------
            is_weapon = any("weapon" in t.lower() for t in types if isinstance(t, str))
            if is_weapon:
                if conf is None:
                    continue
                if float(conf) < 0.50:
                    continue

            safe = safe_doc(r)

            # Pretty confidence
            if safe.get("confidence") is not None:
                try:
                    safe["confidence"] = round(float(safe["confidence"]), 2)
                except:
                    pass

            out.append(safe)

        return jsonify(out)

    except Exception as e:
        current_app.logger.error("Recent Alerts ERROR: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": "alert fetch failed"}), 500


# ---------------------- HEATMAP API ----------------------
@analytics_bp.route("/analytics/heatmap", methods=["GET"])
def analytics_heatmap():
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        pipeline = [
            {"$match": {"date": today}},
            {"$group": {"_id": {"$substr": ["$time", 0, 2]}, "density": {"$avg": "$people_count"}}},
            {"$sort": {"_id": 1}}
        ]

        docs = list(collection.aggregate(pipeline))
        result = [{"hour": d["_id"], "density": round(d["density"] or 0, 2)} for d in docs]

        return jsonify(result)

    except Exception as e:
        current_app.logger.error("HEATMAP ERROR: %s", e)
        return jsonify({"error": "heatmap failed"}), 500


# ---------------------- PERSON REAPPEARANCES ----------------------
@analytics_bp.route("/analytics/reappearances", methods=["GET"])
def analytics_reappearances():
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        pipeline = [
            {"$match": {"date": today, "person_name": {"$ne": None}}},
            {"$group": {"_id": "$person_name", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}},
            {"$sort": {"count": -1}},
        ]

        docs = list(collection.aggregate(pipeline))

        return jsonify([{"person_name": d["_id"], "count": d["count"]} for d in docs])

    except Exception as e:
        current_app.logger.error("REAPPEAR ERROR: %s", e)
        return jsonify({"error": "reappearance failed"}), 500


# ---------------------- VOICE (ENGLISH) ----------------------
@analytics_bp.route("/analytics/voice_summary", methods=["GET"])
def analytics_voice_summary():
    try:
        total_alerts = total_alerts_today()
        criminals_count = unique_criminals_today()
        peak = predict_peak_hour()
        top_loc = most_active_location()

        today = datetime.now().strftime("%Y-%m-%d")
        names = collection.distinct("person_name", {
            "date": today,
            "person_name": {"$ne": None}
        })

        if names:
            criminal_text = f"Detected criminals today: {', '.join(names)}. "
        else:
            criminal_text = "No criminals detected today. "

        text = (
            f"In the last day, {total_alerts} alerts were recorded. "
            f"{criminal_text}"
            f"The busiest time was {peak}. "
            f"Most alerts came from {top_loc}. "
        )

        return jsonify({"text": text})

    except Exception:
        return jsonify({"text": ""}), 500


# ---------------------- VOICE (HINGLISH) ----------------------
@analytics_bp.route("/analytics/voice_summary_hindi", methods=["GET"])
def analytics_voice_summary_hindi():
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        total_alerts = total_alerts_today()
        names = collection.distinct("person_name", {
            "date": today,
            "person_name": {"$ne": None}
        })

        if names:
            criminal_line = f"{len(names)} suspect mile: " + ", ".join(names)
        else:
            criminal_line = "Aaj koi suspect nahi mila"

        peak = predict_peak_hour()
        top_loc = most_active_location()

        text = (
            f"Aaj {total_alerts} alerts aaye. "
            f"{criminal_line}. "
            f"Peak hour: {peak}. Sabse zyada alerts {top_loc} se aaye."
        )

        return jsonify({"text": text})

    except Exception:
        return jsonify({"text": ""}), 500


# ---------------------- PDF GENERATION ----------------------
@analytics_bp.route("/analytics/generate_report", methods=["GET"])
def analytics_generate_report():
    if build_daily_pdf is None:
        return jsonify({"error": "PDF generator missing"}), 500

    try:
        pdf_path = build_daily_pdf()
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify({"error": "PDF failed"}), 500

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        current_app.logger.error("PDF ERROR: %s", e)
        return jsonify({"error": "PDF generation failed"}), 500


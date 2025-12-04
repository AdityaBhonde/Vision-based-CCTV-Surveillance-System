# Backend/report_generator.py
from fpdf import FPDF
from datetime import datetime
import os
from utils.db_utils import total_alerts_today, unique_criminals_today, aggregate_type_counts, most_active_location, predict_peak_hour

def build_daily_pdf(output_filename: str = None) -> str:
    """
    Build a simple daily report PDF and return path.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(0, 10, "Daily Security Report", ln=1, align="C")
    pdf.ln(6)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Generated: {now}", ln=1)
    pdf.ln(6)

    # summary numbers (use your db utils)
    total = total_alerts_today()
    criminals = unique_criminals_today()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Total alerts today: {total}", ln=1)
    pdf.cell(0, 8, f"Unique criminals detected: {criminals}", ln=1)

    pdf.ln(6)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, "Top alert types (7d):", ln=1)
    types = aggregate_type_counts(7)
    for t in types[:8]:
        pdf.cell(0, 7, f" - {t.get('_id', 'unknown')}: {t.get('count', 0)}", ln=1)

    pdf.ln(6)
    pdf.cell(0, 8, f"Peak hour (today): {predict_peak_hour()}", ln=1)
    pdf.cell(0, 8, f"Top location: {most_active_location()}", ln=1)

    # write to file
    if output_filename is None:
        filename = f"security_report_{datetime.now().strftime('%Y%m%d')}.pdf"
    else:
        filename = output_filename

    out_path = os.path.abspath(filename)
    pdf.output(out_path)
    return out_path


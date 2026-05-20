import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import io
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(page_title="RF Generator", layout="centered")
st.title("📄 Reservation Form Generator")

# ==================================================
# TEMPLATE PATH
# ==================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_NAME = "template_fixed.docx"
template_path = os.path.join(BASE_DIR, TEMPLATE_NAME)

if not os.path.exists(template_path):
    st.error("❌ template_fixed.docx not found")
    st.stop()

# ==================================================
# PROJECTS
# ==================================================
projects_data = {
    "SILA": "REQUEST PROPERTIES – L.L.C – S.P.C",
    "SENSI": "NOVA MIDDLE EAST PROPERTY INVESTMENT – L.L.C – S.P.C",
    "BAIA": "REPORTAGE IMPERIAL PROPERTIES LLC",
    "BRABUS TOWNHOUSE": "Flag Al Raha Real Estate Lease and Management Services LLC SPC",
    "BRABUS TOWER": "Flag Al Raha Real Estate Lease and Management Services LLC SPC",
    "THE DISTRICT": "Emirates Reportage Devel and Invest",
    "MARLIN 2": "Reportage Prime Properties LLC-Branch of Abu Dhabi 1",
    "MARLIN": "Reportage Prime Properties LLC-Branch of Abu Dhabi 1",
}

# ==================================================
# HANDOVER DATES
# ==================================================
handover_dates = {
    "SILA": "30-09-2029",
    "SENSI": "30-06-2029",
    "BAIA": "30-09-2029",
    "BRABUS TOWNHOUSE": "30-06-2029",
    "BRABUS TOWER": "30-03-2029",
    "THE DISTRICT": "30-06-2029",
    "MARLIN 2": "30-12-2028",
    "MARLIN": "30-12-2027",
}

# ==================================================
# PAYMENT PLANS
# ==================================================
payment_plans = {
    "30% DP / 5% Disc / 70% Handover": {"dp_pct": 30, "disc": 5, "monthly": 0},
    "30% DP / 0% Disc / 70% Handover": {"dp_pct": 30, "disc": 0, "monthly": 0},
    "5% DP / 5% Disc / 1% Monthly": {"dp_pct": 5, "disc": 5, "monthly": 1},
}

# ==================================================
# PDF GENERATOR (FIXED - NO docx2pdf)
# ==================================================
def generate_pdf(data: dict):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    content = []

    for k, v in data.items():
        content.append(Paragraph(f"<b>{k}</b>: {v}", styles["Normal"]))

    doc.build(content)
    buffer.seek(0)
    return buffer

# ==================================================
# FORM
# ==================================================
with st.form("rf_form"):

    full_name = st.text_input("Full Name")
    nationality = st.text_input("Nationality")
    eid = st.text_input("EID")
    passport = st.text_input("Passport")

    residency_status = st.selectbox("Residency", ["RESIDENCE", "INTERNATIONAL"])
    client_type = st.radio("Client Type", ["Normal", "Investor"])

    project = st.selectbox("Project Name", list(projects_data.keys()))
    developer_name = projects_data[project]

    unit = st.text_input("Unit Number")
    sqft = st.number_input("SQFT", value=0.0)
    price = st.number_input("Price", value=0.0)

    lead_type = st.radio("Lead Type", ["Direct", "Indirect"])

    if lead_type == "Indirect":
        brokerage = st.text_input("Brokerage Company")
        direct_source = ""
    else:
        brokerage = ""
        direct_source = st.selectbox("Direct Source", ["Personal", "Smartsheet"])

    plan_name = st.selectbox("Payment Plan", list(payment_plans.keys()))
    start_date = st.date_input("Start Date", datetime.now())

    handover_date = datetime.strptime(handover_dates[project], "%d-%m-%Y")

    months = max(
        1,
        ((handover_date.year - start_date.year) * 12 +
         (handover_date.month - start_date.month)) + 1
    )

    res_fee = st.number_input("Reservation Fee", value=20000)

    submit = st.form_submit_button("Generate RF")

# ==================================================
# GENERATE
# ==================================================
if submit:

    plan = payment_plans[plan_name]

    selling_price = price * (1 - plan["disc"] / 100)

    dp_amount = selling_price * plan["dp_pct"] / 100

    # 🔥 Deduct reservation fee from DP
    dp_amount = max(0, dp_amount - res_fee)

    monthly_amount = selling_price * plan["monthly"] / 100

    total_monthly = monthly_amount * months

    construction_pct = min(100, plan["dp_pct"] + (months * plan["monthly"]))
    completion_pct = 100 - construction_pct

    construction_amount = selling_price * construction_pct / 100
    completion_amount = selling_price * completion_pct / 100

    end_date = start_date + timedelta(days=30 * months)
    first_month = start_date + timedelta(days=30)

    context = {
        "DATE": datetime.now().strftime("%d/%m/%Y"),
        "Project_Name": project,
        "Developer_Name": developer_name,

        "Full_Name": full_name,
        "Nationality": nationality,
        "ID_Number": eid,
        "Passport_Number": passport,

        "Residency_Status": residency_status,
        "NormalORInvestor":
            "☒ Normal   ☐ Investor" if client_type == "Normal"
            else "☐ Normal   ☒ Investor",

        "Lead_Type": lead_type,
        "Brokerage_company": brokerage if lead_type == "Indirect" else "N/A",
        "Direct_Source": direct_source if lead_type == "Direct" else "",

        "Unit_Number": unit,
        "Total_UNIT": f"{sqft:,.2f} sqft",

        "total_purchase_price": f"{selling_price:,.2f}",

        "Reservation_Fee": f"{res_fee:,.2f}",

        "dp_amount": f"{dp_amount:,.2f}",
        "dp_pct": f"{plan['dp_pct']}%",

        "monthly_amount": f"{monthly_amount:,.0f}",
        "months_count": months,
        "total_monthly_amount": f"{total_monthly:,.0f}",

        "start_date": start_date.strftime("%d-%m-%Y"),
        "end_date": end_date.strftime("%d-%m-%Y"),
        "first_monthly_date": first_month.strftime("%d-%m-%Y"),

        "Total_Construction_pct": f"{construction_pct}%",
        "total_purchase_Construction": f"{construction_amount:,.2f}",

        "Completion_pct": f"{completion_pct}%",
        "Completion_amount": f"{completion_amount:,.2f}",
    }

    # =========================
    # WORD
    # =========================
    doc = DocxTemplate(template_path)

    doc.render(context)

    word_buffer = io.BytesIO()
    doc.save(word_buffer)
    word_buffer.seek(0)
    word_bytes = word_buffer.getvalue()

    # =========================
    # PDF (FIXED)
    # =========================
    pdf_buffer = generate_pdf(context)

    # =========================
    # DOWNLOAD
    # =========================
    st.success("RF Generated Successfully")

    st.download_button(
        "⬇️ Download Word",
        word_bytes,
        file_name=f"{project}_{unit}.docx"
    )

    st.download_button(
        "⬇️ Download PDF",
        pdf_buffer,
        file_name=f"{project}_{unit}.pdf"
    )

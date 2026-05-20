import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import io
import os
from docx2pdf import convert
import tempfile

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
    "REPORTAGE TOWER": "Reportage Global Real Estate Development LLC",
    "VISTA 3": "Reportage Prime Properties LLC-Branch of Abu Dhabi 1",
    "MV1": "Webridge Properties LLC",
    "MV2": "Sama Emirates Holding Group LLC",
    "ROYAL PARK": "Sama Emirates Properties SP LLC",
    "SELINA BAY": "Century 7 Properties LLC Branch of Abu Dhabi 1",
    "KHALIFA": "REPORTAGE VILLAGE ABU DHABI - Reportage Prime Properties LLC-Branch of Abu Dhabi 1",
    "PERLA 3": "Emirates Reportage Development and Investments LLC",
    "PERLA 2": "Reportage Line Properties LLC",
    "PERLA 1": "Reportage Line Properties LLC",
    "PLAZA 2": "Reportage Prime Properties LLC-Branch of Abu Dhabi 1",
    "PLAZA 1": "Reportage Prime Properties LLC-Branch of Abu Dhabi 1",
    "DIVA 1 & 2": "Webridge Properties L.L.C",
    "AL RAHA 1 LOFTS 1": "Reportage Investment LLC",
    "AL RAHA 2 LOFTS 2": "Reportage Investment LLC",
    "OASIS 1": "Elige Real Estate LLC",
    "OASIS 2": "Reportage Prime Properties LLC-Branch of Abu Dhabi 1",
    "THE GATE": "Reportage Hospitality Real Estate Limited",
    "VERDANA 6W TOWNHOUSE": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 6X TOWNHOUSE": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 6Y TOWNHOUSE": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 3K RESIDENCE": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 3L RESIDENCE": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 3M RESIDENCE": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 3N RESIDENCE": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 3N TOWNHOUSE": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 3O RESIDENCES": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 3O TOWNHOUSE": "REPORTAGE PLUS A REAL ESTATE DEVELOPMENT",
    "VERDANA 10 RESIDENCE": "Reportage Prime Properties LLC",
    "VERDANA 10 TOWNHOUSE": "Reportage Prime Properties LLC",
    "VERDANA 9 RESIDENCE": "Reportage Prime Properties LLC",
    "VERDANA 9 TOWNHOUSE": "Reportage Prime Properties LLC",
    "VERDANA 8 RESIDENCE": "Reportage Prime Properties LLC",
    "VERDANA 8 TOWNHOUSE": "Reportage Prime Properties LLC",
    "VERDANA 7 RESIDENCE": "Reportage Prime Properties LLC",
    "VERDANA 7 TOWNHOUSE": "Reportage Prime Properties LLC",
    "VERDANA 5 RESIDENCE": "Reportage Prime Properties LLC",
    "VERDANA 5 TOWNHOUSE": "Reportage Prime Properties LLC",
    "VERDANA 4 RESIDENCE": "Reportage Prime Properties LLC",
    "VERDANA 4 TOWNHOUSE": "Reportage Prime Properties LLC",
    "VERDANA 3 RESIDENCE": "Reportage Prime Properties LLC",
    "VERDANA 3 TOWNHOUSE": "Reportage Prime Properties LLC",
    "VERDANA 2 RESIDENCE": "Reportage Prime Properties LLC",
    "VERDANA 2 TOWNHOUSE": "Reportage Prime Properties LLC",
    "VERDANA 1 RESIDENCE": "Reportage Prime Properties LLC",
    "VERDANA 1 TOWNHOUSE": "Reportage Prime Properties LLC",
    "REPORTAGE HILLS": "Reportage Prime Properties LLC",
    "TAORMINA VILLAGE 2": "Reportage Prime Properties LLC",
    "TAORMINA VILLAGE 1": "Reportage Prime Properties LLC",
    "REPORTAGE VILLAGE": "Reportage Prime Properties LLC",
    "BIANCA": "Reportage Prime Properties LLC",
    "ALBA": "Century Seven Properties LLC",
    "RUKAN TOWER": "Reportage Prime Properties LLC",
    "ALEXIS TOWER": "Reportage Prime Properties LLC",
    "RUKAN LOFT 2": "Reportage Prime Properties LLC",
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
    "REPORTAGE TOWER": "30-12-2028",
    "VISTA 3": "30-12-2027",
    "MV1": "30-12-2025",
    "MV2": "30-12-2026",
    "ROYAL PARK": "30-12-2027",
    "SELINA BAY": "30-12-2027",
    "KHALIFA": "30-09-2028",
    "PERLA 3": "30-06-2027",
    "PERLA 2": "30-12-2026",
    "PERLA 1": "30-12-2028",
    "PLAZA 2": "30-06-2026",
    "PLAZA 1": "30-12-2026",
}

# ==================================================
# PAYMENT PLANS
# ==================================================
payment_plans = {
    "30% DP / 5% Disc / 70% Handover": {"dp_pct": 30, "disc": 5, "monthly": 0},
    "30% DP / 0% Disc / 70% Handover": {"dp_pct": 30, "disc": 0, "monthly": 0},
    "5% DP / 5% Disc / 1% Monthly": {"dp_pct": 5, "disc": 5, "monthly": 1},
    "5% DP / 0% Disc / 1% Monthly": {"dp_pct": 5, "disc": 0, "monthly": 1},
    "10% DP / 5% Disc / 1% Monthly": {"dp_pct": 10, "disc": 5, "monthly": 1},
    "20% DP / 15% Disc / 1% Monthly": {"dp_pct": 20, "disc": 15, "monthly": 1},
}

# ==================================================
# FORM
# ==================================================
with st.form("rf_form"):
    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input("Full Name")
        nationality = st.text_input("Nationality")
        eid = st.text_input("EID")
        passport = st.text_input("Passport")
        address = st.text_input("Address")
        phone = st.text_input("Phone")
        email = st.text_input("Email")

        residency_status = st.selectbox("Residency", ["RESIDENCE", "INTERNATIONAL"])
        client_type = st.radio("Client Type", ["Normal", "Investor"])

    with col2:
        project = st.selectbox("Project Name", list(projects_data.keys()))
        developer_name = projects_data[project]

        unit = st.text_input("Unit Number")
        unit_type = st.text_input("Unit Type")
        view = st.text_input("View")
        sqft = st.number_input("SQFT", value=0.0)
        price = st.number_input("Price", value=0.0)

    st.subheader("Sales Info")
    pc_name = st.text_input("PC Name")

    lead_type = st.radio("Lead Type", ["Direct", "Indirect"])

    if lead_type == "Indirect":
        brokerage = st.text_input("Brokerage Company")
        direct_source = ""
    else:
        direct_source = st.selectbox("Direct Source", ["Personal", "Smartsheet"])
        brokerage = ""

    st.subheader("Payment")
    plan_name = st.selectbox("Plan", list(payment_plans.keys()))
    start_date = st.date_input("Start Date", datetime.now())

    handover_date = datetime.strptime(handover_dates[project], "%d-%m-%Y")

    months = max(
        1,
        ((handover_date.year - start_date.year) * 12 +
         (handover_date.month - start_date.month)) + 1
    )

    st.number_input("Months", value=months, disabled=True)

    res_fee = st.number_input("Reservation Fee", value=20000)
    reg_option = st.selectbox("Fees", ["DLD", "ADM", "ADGM"])

    submit = st.form_submit_button("Generate RF")

# ==================================================
# GENERATE
# ==================================================
if submit:

    plan = payment_plans[plan_name]

    selling_price = price * (1 - plan["disc"] / 100)

    dp_amount = selling_price * plan["dp_pct"] / 100

    monthly_amount = selling_price * plan["monthly"] / 100

    total_monthly = monthly_amount * months

    construction_pct = min(100, plan["dp_pct"] + (months * plan["monthly"]))
    completion_pct = 100 - construction_pct

    construction_amount = selling_price * construction_pct / 100
    completion_amount = selling_price * completion_pct / 100

    # 🔥 reservation deducted from DP
    dp_amount = max(0, dp_amount - res_fee)

    end_date = start_date + timedelta(days=30 * months)
    first_monthly = start_date + timedelta(days=30)

    if reg_option == "DLD":
        gov_fee = price * 0.04 + 1193.15
    elif reg_option == "ADM":
        gov_fee = price * 0.02 + 625
    else:
        gov_fee = price * 0.02 + 5625

    doc = DocxTemplate(template_path)

    context = {
        "DATE": datetime.now().strftime("%d/%m/%Y"),
        "Project_Name": project,
        "Developer_Name": developer_name,

        "Full_Name": full_name,
        "Home_Address": address,
        "Email_Address": email,
        "Mobile_Number": phone,
        "ID_Number": eid,
        "Nationality": nationality,
        "Passport_Number": passport,

        "Residency_Status": residency_status,

        "NormalORInvestor":
            "☒ Normal   ☐ Investor" if client_type == "Normal"
            else "☐ Normal   ☒ Investor",

        "Lead_Type": lead_type,
        "Brokerage_company": brokerage if lead_type == "Indirect" else "N/A",
        "Direct_Source": direct_source if lead_type == "Direct" else "",

        "Unit_Number": unit,
        "Unit_Type_BHK": unit_type,
        "View": view,
        "Total_UNIT": f"{sqft:,.2f} sqft",

        "PC_Name": pc_name,

        "total_purchase_price": f"{selling_price:,.2f}",

        "Reservation_Fee": f"{res_fee:,.2f}",

        "dp_amount": f"{dp_amount:,.2f}",
        "dp_pct": f"{plan['dp_pct']}%",

        "monthly_amount": f"{monthly_amount:,.0f}",
        "months_count": months,
        "total_monthly_amount": f"{total_monthly:,.0f}",

        "start_date": start_date.strftime("%d-%m-%Y"),
        "end_date": end_date.strftime("%d-%m-%Y"),
        "first_installment": first_monthly.strftime("%d-%m-%Y"),

        "Total_Construction_pct": f"{construction_pct}%",
        "total_purchase_Construction": f"{construction_amount:,.2f}",

        "Completion_pct": f"{completion_pct}%",
        "Completion_amount": f"{completion_amount:,.2f}",

        "GOV_FEES": f"{gov_fee:,.2f}",
    }

    doc.render(context)

    # =========================
    # WORD OUTPUT
    # =========================
    word_stream = io.BytesIO()
    doc.save(word_stream)
    word_stream.seek(0)
    word_bytes = word_stream.getvalue()

    # =========================
    # PDF OUTPUT
    # =========================
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    tmp.write(word_bytes)
    tmp.close()

    pdf_path = tmp.name.replace(".docx", ".pdf")
    convert(tmp.name, pdf_path)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    st.success("Generated Successfully")

    st.download_button("⬇️ Download Word", word_bytes,
                       file_name=f"{project}_{unit}.docx")

    st.download_button("⬇️ Download PDF", pdf_bytes,
                       file_name=f"{project}_{unit}.pdf")

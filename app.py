import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="RF Generator", layout="centered")

st.title("📄 Reservation Form Generator")

# 🔥 Payment Plans
payment_plans = {
    "30% DP / 5% Disc / 70% Handover": {"dp_pct": 30, "disc": 5, "monthly": 0},
    "30% DP / 0% Disc / 70% Handover": {"dp_pct": 30, "disc": 0, "monthly": 0},
    "5% DP / 5% Disc / 1% Monthly": {"dp_pct": 5, "disc": 5, "monthly": 1},
    "5% DP / 0% Disc / 1% Monthly": {"dp_pct": 5, "disc": 0, "monthly": 1},
    "10% DP / 5% Disc / 1% Monthly": {"dp_pct": 10, "disc": 5, "monthly": 1},
    "20% DP / 15% Disc / 1% Monthly": {"dp_pct": 20, "disc": 15, "monthly": 1},
    "25% Discount Cash": {"dp_pct": 100, "disc": 25, "monthly": 0},
    "30% Discount Cash": {"dp_pct": 100, "disc": 30, "monthly": 0},
    "No discount (Full in 1 month)": {"dp_pct": 100, "disc": 0, "monthly": 0},
}

with st.form("form"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Client Info")
        full_name = st.text_input("Full Name")
        eid = st.text_input("EID")
        passport = st.text_input("Passport")
        address = st.text_input("Address")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        client_type = st.radio("Client Type", ["Normal", "Investor"])

    with col2:
        st.subheader("🏠 Unit Info")
        project = st.text_input("Project Name")
        unit = st.text_input("Unit Number")
        unit_type = st.text_input("Unit Type")
        view = st.text_input("View")
        sqft = st.number_input("SQFT", value=0.0)
        price = st.number_input("Price", value=0.0)

    st.subheader("💼 Sales Info")
    pc_name = st.text_input("PC Name")
    lead_type = st.radio("Lead Type", ["Direct", "Indirect"])
    brokerage = st.text_input("Brokerage Company") if lead_type == "Indirect" else "Direct"

    st.subheader("💰 Payment")
    plan_name = st.selectbox("Payment Plan", list(payment_plans.keys()))
    start_date = st.date_input("Start Date", datetime.now())
    months = st.number_input("Installments Months", value=42)
    res_fee = st.number_input("Reservation Fee", value=20000)

    reg_option = st.selectbox("Registration Fee", ["DLD", "ADM", "ADGM"])

    submit = st.form_submit_button("Generate RF")

# 🚀 Generate File
if submit:
    plan = payment_plans[plan_name]

    selling_price = price * (1 - plan["disc"]/100)
    dp_amount = selling_price * (plan["dp_pct"]/100)
    monthly_amount = selling_price * (plan["monthly"]/100)
    total_monthly = monthly_amount * months
    end_date = start_date + timedelta(days=30*months)

    # Gov Fees
    if reg_option == "DLD":
        gov_fee = price * 0.04 + 1193.15
    elif reg_option == "ADM":
        gov_fee = price * 0.02 + 625
    else:
        gov_fee = price * 0.02 + 5625

    doc = DocxTemplate("2026-RF-TEMP-FIXED.docx")

    context = {
        "DATE": datetime.now().strftime("%d/%m/%Y"),
        "Project_Name": project,
        "Project Name": project,
        "Full_Name": full_name,
        "Home_Address": address,
        "Email_Address": email,
        "Mobile_Number": phone,
        "ID_Number": eid,
        "Nationality": "",
        "Passport_Number": passport,

        "Residency_Status": "☒ Normal   ☐ Investor" if client_type=="Normal" else "☐ Normal   ☒ Investor",
        "residency_status": "☒ Normal   ☐ Investor" if client_type=="Normal" else "☐ Normal   ☒ Investor",

        "total_purchase_price": f"{selling_price:,.2f}",
        "Unit_Number": unit,
        "Unit_Type_BHK": unit_type,
        "View": view,
        "DET_UNITS": "Residential",
        "Total_UNIT": f"{sqft:,.2f} sqft",

        "PC_Name": pc_name,
        "Brokerage_company": brokerage,

        "Reservation_Fee": f"{res_fee:,.2f}",
        "res_pct": "-",
        "dp_pct": f"{plan['dp_pct']}%",
        "dp_date": start_date.strftime("%d/%m/%Y"),
        "dp_amount": f"{dp_amount:,.2f}",

        "monthly_amount": f"{monthly_amount:,.0f}",
        "months_count": months,
        "total_monthly_amount": f"{total_monthly:,.0f}",
        "total_monthly_pct": f"{months}%",

        "start_date": start_date.strftime("%d-%b-%Y"),
        "end_date": end_date.strftime("%d-%b-%Y"),

        "Total_Construction_pct": f"{plan['dp_pct'] + (months if plan['monthly']>0 else 0)}%",
        "Completion_pct": f"{100 - (plan['dp_pct'] + (months if plan['monthly']>0 else 0))}%",

        "GOV FEES": f"{gov_fee:,.2f}"
    }

    doc.render(context)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    st.success("✅ File جاهز")

    st.download_button(
        label="⬇️ Download RF",
        data=file_stream,
        file_name=f"{project}_{unit}_{full_name}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

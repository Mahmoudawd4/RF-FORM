import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import io
import os

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="RF Generator",
    layout="centered"
)

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
# PROJECTS & DEVELOPERS
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
}

# ==================================================
# PAYMENT PLANS
# ==================================================
payment_plans = {
    "30% DP / 5% Disc / 70% Handover": {"dp_pct": 30, "disc": 5, "monthly": 0},
    "30% DP / 0% Disc / 70% Handover": {"dp_pct": 30, "disc": 0, "monthly": 0},
    "5% DP / 5% Disc / 1% Monthly": {"dp_pct": 5, "disc": 5, "monthly": 1},
    "10% DP / 5% Disc / 1% Monthly": {"dp_pct": 10, "disc": 5, "monthly": 1},
}

# ==================================================
# FORM
# ==================================================
with st.form("rf_form"):

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Client Info")
        full_name = st.text_input("Full Name")
        nationality = st.text_input("Nationality")
        eid = st.text_input("EID")
        passport = st.text_input("Passport")
        address = st.text_input("Address")
        phone = st.text_input("Phone")
        email = st.text_input("Email")

        residency_status = st.selectbox("Residency Status", ["RESIDENCE", "INTERNATIONAL"])
        client_type = st.radio("Client Type", ["Normal", "Investor"])

    with col2:
        st.subheader("🏠 Unit Info")
        project = st.selectbox("Project Name", list(projects_data.keys()))
        developer_name = projects_data[project]

        st.text_input("Developer Name", value=developer_name, disabled=True)

        unit = st.text_input("Unit Number")
        unit_type = st.text_input("Unit Type")
        view = st.text_input("View")
        sqft = st.number_input("SQFT", value=0.0)
        price = st.number_input("Price", value=0.0)

    # ==============================================
    # SALES INFO
    # ==============================================
    st.subheader("💼 Sales Info")

    pc_name = st.text_input("PC Name")
    lead_type = st.radio("Lead Type", ["Direct", "Indirect"])

    if lead_type == "Indirect":
        direct_source = ""
        brokerage = "{{Brokerage_company}}"
    else:
        direct_source = st.selectbox("Direct Source", ["Personal", "Smartsheet"])
        brokerage = ""

    # ==============================================
    # PAYMENT
    # ==============================================
    st.subheader("💰 Payment")

    plan_name = st.selectbox("Payment Plan", list(payment_plans.keys()))
    start_date = st.date_input("Start Date", datetime.now())

    handover_date = datetime.strptime(handover_dates[project], "%d-%m-%Y")

    months = max(
        1,
        (
            (handover_date.year - start_date.year) * 12 +
            (handover_date.month - start_date.month)
        )
    )

    st.number_input("Installments Months", value=months, disabled=True)

    res_fee = st.number_input("Reservation Fee", value=20000)
    reg_option = st.selectbox("Registration Fee", ["DLD", "ADM", "ADGM"])

    submit = st.form_submit_button("Generate RF")

# ==================================================
# GENERATE FILE
# ==================================================
if submit:
    try:
        plan = payment_plans[plan_name]

        selling_price = price * (1 - plan["disc"] / 100)

        # ✅ DP after deducting reservation fee
        dp_amount = (selling_price * (plan["dp_pct"] / 100)) - res_fee
        dp_amount = max(dp_amount, 0)

        monthly_amount = selling_price * (plan["monthly"] / 100)
        total_monthly = monthly_amount * months

        construction_pct = min(100, plan["dp_pct"] + (months * plan["monthly"]))
        completion_pct = 100 - construction_pct

        construction_amount = selling_price * construction_pct / 100
        completion_amount = selling_price * completion_pct / 100

        end_date = start_date + relativedelta(months=months)

        # ✅ First installment starts after 1 month
        first_installment_date = start_date + relativedelta(months=1)

        # GOV FEES
        if reg_option == "DLD":
            gov_fee = (price * 0.04 + 1193.15)
        elif reg_option == "ADM":
            gov_fee = (price * 0.02 + 625)
        else:
            gov_fee = (price * 0.02 + 5625)

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
            "total_purchase_price": f"{selling_price:,.2f}",
            "Unit_Number": unit,
            "Unit_Type_BHK": unit_type,
            "View": view,
            "Total_UNIT": f"{sqft:,.2f} sqft",
            "PC_Name": pc_name,
            "Lead_Type": lead_type,

            # ✅ brokerage logic fixed
            "Brokerage_company": brokerage,

            "Direct_Source": direct_source,
            "Reservation_Fee": f"{res_fee:,.2f}",

            "dp_pct": f"{plan['dp_pct']}%",
            "dp_date": start_date.strftime("%d/%m/%Y"),
            "dp_amount": f"{dp_amount:,.2f}",

            "monthly_amount": f"{monthly_amount:,.0f}",
            "months_count": months,
            "total_monthly_amount": f"{total_monthly:,.0f}",

            "start_date": start_date.strftime("%d-%b-%Y"),
            "end_date": end_date.strftime("%d-%b-%Y"),

            # ✅ new field
            "first_installment_date": first_installment_date.strftime("%d-%b-%Y"),

            "Total_Construction_pct": f"{construction_pct}%",
            "total_purchase_Construction": f"{construction_amount:,.2f}",
            "Completion_pct": f"{completion_pct}%",
            "Completion_amount": f"{completion_amount:,.2f}",

            "NormalORInvestor": (
                "☒ Normal ☐ Investor" if client_type == "Normal"
                else "☐ Normal ☒ Investor"
            ),

            "GOV_FEES": f"{gov_fee:,.2f}",
        }

        doc.render(context)

        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)

        st.success("✅ RF Generated Successfully")

        st.download_button(
            label="⬇️ Download RF",
            data=file_stream,
            file_name=f"{project}_{unit}_{full_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

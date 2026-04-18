import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import io

# إعدادات الصفحة
st.set_page_config(page_title="Reportage Form Generator", layout="centered")

st.title("📄 Reportage - Reservation Form Generator")
st.info("قم بتعبئة البيانات أدناه لاستخراج عقد الحجز (RF) بصيغة Word")

# 1. تعريف خطط الدفع (المعطيات التي ذكرتها سابقاً)
payment_plans = {
    "30% DP / 5% Disc / 70% Handover": {"dp_pct": 30, "disc": 5},
    "5% DP / 5% Disc / 1% Monthly": {"dp_pct": 5, "disc": 5},
    "10% DP / 5% Disc / 1% Monthly": {"dp_pct": 10, "disc": 5},
    "20% DP / 15% Disc / 1% Monthly": {"dp_pct": 20, "disc": 15},
    "25% Discount Cash": {"dp_pct": 100, "disc": 25},
    "No discount (Full in 1 month)": {"dp_pct": 100, "disc": 0},
}

# 2. واجهة الإدخال
with st.form("main_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 بيانات العميل")
        full_name = st.text_input("Full_Name")
        id_number = st.text_input("ID_Number")
        passport = st.text_input("Passport_Number")
        nationality = st.text_input("Nationality")
        phone = st.text_input("Mobile_Number")
        email = st.text_input("Email_Address")
        address = st.text_input("Home_Address")
        client_type = st.radio("residency_status", ["Normal", "Investor"])

    with col2:
        st.subheader("🏠 بيانات الوحدة")
        project_name = st.text_input("Project_Name", value="THE DISTRICT")
        unit_number = st.text_input("Unit_Number")
        unit_type = st.text_input("Unit_Type_BHK")
        view = st.text_input("View")
        sqft = st.number_input("Total_UNIT", value=0.0)
        original_price = st.number_input("total_purchase_price", value=0.0)
        parking = st.selectbox("Parking Option", ["None", "Pay Now (50k)", "Pay at Handover (70k)"])

    st.subheader("💰 خطة الدفع")
    selected_plan = st.selectbox("Select Payment Plan", list(payment_plans.keys()))
    start_date = st.date_input("Installments Start Date", value=datetime.now())
    months_count = st.number_input("Number of Installment Months", value=42)
    res_fee = st.number_input("Reservation Fee", value=20000)
    
    reg_fee_option = st.selectbox("Registration Fee (DLD/ADM)", [
        "DLD: 4% + AED 1,193.15",
        "ADM: 2% + AED 625",
        "ADGM ADM: 2% + AED 5625"
    ])

    submit_button = st.form_submit_button("Generate Document")

if submit_button:
    try:
        # --- العمليات الحسابية ---
        plan = payment_plans[selected_plan]
        
        # حساب السعر بعد الخصم
        selling_price = original_price * (1 - plan["disc"] / 100)
        
        # حساب الباركنج (دفع الآن يضاف للسعر)
        parking_added = 50000 if parking == "Pay Now (50k)" else 0
        total_purchase_price = selling_price + parking_added
        
        # حساب الدفعة الأولى (Down Payment)
        dp_amount = selling_price * (plan["dp_pct"] / 100)
        
        # حساب الأقساط الشهرية (التجميعية كما طلبت)
        # نفترض أن القسط 1% من الـ Selling Price
        monthly_val = selling_price * 0.01 
        total_monthly_sum = monthly_val * months_count
        
        # حساب تاريخ الانتهاء
        end_date = start_date + timedelta(days=30 * months_count)

        # --- ملء القالب ---
        doc = DocxTemplate("2026-RF-TEMP (1) (1).docx")
        
        context = {
            "DATE": datetime.now().strftime("%d/%m/%Y"),
            "Full Name": Full_Name,
            "Home Address": Home_Address,
            "Email Address": Email_Address,
            "Mobile Number": Mobile_Number,
            "ID Number": ID_Number,
            "Passport Number": Passport_Number,
            "Nationality": Nationality,
            "Project Name": Project_Name,
            "Unit Number": Unit_Number,
            "MANY bhk": Unit_Type_BHK,
            "VIEW": view,
            "Total UNIT": f"{sqft:,.2f} sqft",
            "total_purchase_price": f"{total_purchase_price:,.2f}",
            "residency_status": "☒" if client_type == "Normal" else "☐",
            "PC Name": "Sales Team",
            "Brokerage company": "Direct" if "Direct" in selected_plan else "Agent",
            
            # بيانات الجدول (التجميعية)
            "monthly_amount": f"{monthly_val:,.0f}",
            "months_count": int(months_count),
            "total_monthly_amount": f"{total_monthly_sum:,.0f}",
            "total_monthly_pct": f"{months_count}%",
            "start_date": start_date.strftime("%d-%B-%Y"),
            "end_date": end_date.strftime("%d-%B-%Y"),
            "reservation_fee": f"{res_fee:,.2f}",
            "dp_amount": f"{dp_amount:,.2f}",
            "dp_pct": f"{plan['dp_pct']}%",
            "GOV_FEES": reg_fee_option
        }

        # إنشاء الملف في الذاكرة
        doc.render(context)
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)

        st.success("✅ تم تجهيز الملف بنجاح!")
        st.download_button(
            label="⬇️ Download Reservation Form (Word)",
            data=bio,
            file_name=f"RF_{full_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        st.error(f"حدث خطأ: {e}")

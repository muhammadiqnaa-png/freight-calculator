import streamlit as st
import math
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime
import requests
import streamlit as st

# ==========================================================
# ⚙️ Page Config (WAJIB paling atas!)
# ==========================================================
st.set_page_config(
    page_title="Freight Calculator Barge",
    page_icon="https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/icon-512x512.png",
    layout="centered"
)

st.markdown("""
<style>
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 🔧 PWA Support — biar bisa di-install di HP
# ==========================================================
st.markdown("""
<link rel="manifest" href="https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/manifest.json">
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/service-worker.js')
    .then(reg => console.log("Service worker registered:", reg))
    .catch(err => console.log("Service worker failed:", err));
}
</script>
""", unsafe_allow_html=True)

# ==========================================================
# 🍎 iPhone (Safari) Support — tambahan meta
# ==========================================================
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="FreightCalc">
""", unsafe_allow_html=True)


# ====== FIREBASE AUTH ======
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]
AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
REGISTER_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

def login_user(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def register_user(email, password):
    res = requests.post(REGISTER_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

# ===== LOGIN =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>🔐 Login Freight Calculator</h2>", unsafe_allow_html=True)
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login 🚀"):
            ok, data = login_user(email, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Email or password incorrect!")

    with tab_register:
        email = st.text_input("Email Register")
        password = st.text_input("Password Register", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(email, password)
            if ok:
                st.success("Registration successful! Please login.")
            else:
                st.error("Failed to register. Email may already exist.")
    st.stop()


# ==========================================================
# ⚙️ PRESET PARAMETER KAPAL (non-intrusive)
# - ditaruh di expander sidebar yang default tertutup
# - tidak mengubah layout main / posisi expander lain
# ==========================================================
preset_params = {
    "270 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 85, "price_fuel": 13500,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 40000000,
        "docking": 40000000, "maintenance": 40000000,
        "certificate": 40000000, "premi_nm": 50000, "other_cost": 10000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 4, "port_stay_pod": 4
    },
    "300 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 115, "price_fuel": 13500,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 50000000,
        "docking": 50000000, "maintenance": 50000000,
        "certificate": 45000000, "premi_nm": 50000, "other_cost": 15000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 5, "port_stay_pod": 5
    },
    "330 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 130, "price_fuel": 13500,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 60000000,
        "docking": 60000000, "maintenance": 60000000,
        "certificate": 50000000, "premi_nm": 50000, "other_cost": 20000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 5, "port_stay_pod": 5
    }
}

# ==== PRESET SEGMEN ====

# Default state
if "preset_selected" not in st.session_state:
    st.session_state.preset_selected = "Custom"

# Handler untuk update state
def update_preset():
    st.session_state.preset_selected = st.session_state.preset_control

preset = st.sidebar.segmented_control(
    "Size Barge",
    ["270 ft", "300 ft", "330 ft", "Custom"],
    default=st.session_state.preset_selected,
    key="preset_control",
    on_change=update_preset
)

# ==== APPLY PRESET ====
if st.session_state.preset_selected != "Custom":
    chosen = preset_params[st.session_state.preset_selected]
    for k, v in chosen.items():
        st.session_state[k] = v


st.subheader("📱 Menu")

    menu = st.radio(
        "",
        ["🧮 Calculator", "⚙️ Parameter", "👤 Account"],
        horizontal=True
    )

    if menu == "🧮 Calculator":



        # ===== PDF GENERATOR =====
        def create_pdf(username):
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=25,
                leftMargin=25,
                topMargin=0,
                bottomMargin=0
            )

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='HeaderBlue', fontSize=16, textColor=colors.HexColor("#0d47a1"), alignment=1, spaceAfter=4))
            styles.add(ParagraphStyle(name='SubHeader', fontSize=12, textColor=colors.HexColor("#0d47a1"), spaceAfter=4, fontName='Helvetica-Bold'))
            styles.add(ParagraphStyle(name='NormalSmall', fontSize=8, leading=12))
            styles.add(ParagraphStyle(name='Bold', fontSize=11, fontName='Helvetica-Bold'))

            elements = []
            def fmt_rp(x):
                return f"Rp {x:,.0f}"

            def pct_of_total(x):
                try:
                    if total_cost and total_cost > 0:
                        return f"   ({(x / total_cost) * 100:.1f}%)"
                    else:
                        return " (0.0%)"
                except Exception:
                    return " (0.0%)"

            # ===== HEADER =====
            title = Paragraph("<b>Freight Calculation Report</b>", styles['HeaderBlue'])
            elements.append(title)
            elements.append(Spacer(1, 2))

            # ===== VOYAGE INFO =====
            elements.append(Paragraph("Voyage Information", styles['SubHeader']))
            voyage_data = [
                ["Port Of Loading", port_pol],
                ["Port Of Discharge", port_pod],
                ["Next Port", next_port],
                ["Cargo Quantity", f"{qyt_cargo:,.0f} {type_cargo.split()[1]}"],
                ["Distance (NM)", f"{distance_pol_pod:,.0f}"],
                ["Total Voyage (Days)", f"{total_voyage_days:.2f}"],
            ]
            t_voyage = Table(voyage_data, colWidths=[9*cm, 9*cm])
            t_voyage.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements += [t_voyage, Spacer(1, 4)]

            # ===== OPERATIONAL COST =====
            elements.append(Paragraph("Operational & Cost Summary", styles['SubHeader']))
            calc_data = [
                ["Total Sailing Time (Hour)", f"{sailing_time:.2f}"],
                ["Total Consumption Fuel (Ltr)", f"{total_consumption_fuel:,.0f}"],
                ["Total Consumption Freshwater (Ton)", f"{total_consumption_fw:,.0f}"],
                ["Fuel Cost (Rp)", f"{fmt_rp(cost_fuel)}{pct_of_total(cost_fuel)}"],
                ["Freshwater Cost (Rp)", f"{fmt_rp(cost_fw)}{pct_of_total(cost_fw)}"],
                ["Total General Overhead (Voyage)", fmt_rp(total_general_overhead) + pct_of_total(total_general_overhead)],
            ]

            for k, v in owner_data.items():
                calc_data.append([k, f"{fmt_rp(v)}{pct_of_total(v)}"])

            if additional_breakdown:
                calc_data.append(["--- Additional Costs ---", ""])
                for k, v in additional_breakdown.items():
                    calc_data.append([k, f"{fmt_rp(v)}{pct_of_total(v)}"])

            calc_data.append(["Total Cost (Rp)", f"Rp {total_cost:,.0f}"])
            calc_data.append([f"Freight Cost ({type_cargo.split()[1]})", f"Rp {freight_cost_mt:,.0f}"])

            t_calc = Table(calc_data, colWidths=[9*cm, 9*cm])
            t_calc.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements += [t_calc, Spacer(1, 4)]

            # ===== FREIGHT PRICE =====
            if freight_price_input > 0:
                elements.append(Paragraph("Freight Price Calculation User", styles['SubHeader']))
                fpc_data = [
                    ["Freight Price (Rp/MT)", f"Rp {freight_price_input:,.0f}"],
                    ["Revenue", f"Rp {revenue_user:,.0f}"],
                    ["PPH 1.2%", f"Rp {pph_user:,.0f}"],
                    ["Profit", f"Rp {profit_user:,.0f}"],
                    ["Profit %", f"{profit_percent_user:.2f} %"],
                ]
                t_fpc = Table(fpc_data, colWidths=[9*cm, 9*cm])
                t_fpc.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                ]))
                elements += [t_fpc, Spacer(1, 4)]

            # ===== TCE =====
            elements.append(Paragraph("Time Charter Equivalent (TCE)", styles['SubHeader']))

            tce_data = [
                ["Base Cost (Fuel + FW + Port + Premi)", fmt_rp(tce_base_cost)],
                ["TCE Per Day", f"{fmt_rp(tce_per_day)} / Day"],
                ["TCE Per Month", f"{fmt_rp(tce_per_month)} / Month"],
            ]

            t_tce = Table(tce_data, colWidths=[9*cm, 9*cm])
            t_tce.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))

            elements += [t_tce, Spacer(1, 4)]


            # ===== PROFIT SCENARIO =====
            elements.append(Paragraph("Profit Scenario 0–75%", styles['SubHeader']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t_profit = Table(profit_table, colWidths=[3*cm, 3.8*cm, 3.8*cm, 3.8*cm, 3.8*cm])
            t_profit.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements += [t_profit, Spacer(1, 4)]

            # ===== FOOTER =====
            footer_text = f"Generated by {username} | https://freight-calculator-barge-byiqna.streamlit.app/"
            elements.append(Paragraph(footer_text, styles['NormalSmall']))

            # Tanggal generated di bawah footer
            generated_date = Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", styles['NormalSmall'])
            elements.append(generated_date)

            # ===== BUILD PDF =====
            doc.build(elements)
            buffer.seek(0)
            return buffer

        # ===== GENERATE PDF & DOWNLOAD BUTTON =====
        pdf_buffer = create_pdf(username=st.session_state.email)
        file_name = f"Freight_Report_{port_pol}_{port_pod}_{datetime.now():%Y%m%d}.pdf"

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")

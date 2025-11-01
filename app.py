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
    layout="wide"
)

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

# ===== LOGOUT =====
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Successfully logged out.")
    st.rerun()

# ===== MODE =====
mode = st.sidebar.selectbox("Mode", ["Owner", "Charter"])

# ===== SIDEBAR PARAMETERS =====
with st.sidebar.expander("🚢 Speed"):
    speed_laden = st.number_input("Speed Laden (knot)", 0.0)
    speed_ballast = st.number_input("Speed Ballast (knot)", 0.0)

with st.sidebar.expander("⛽ Fuel"):
    consumption = st.number_input("Consumption Fuel (liter/hour)", 0)
    price_fuel = st.number_input("Price Fuel (Rp/Ltr)", 0)

with st.sidebar.expander("💧 Freshwater"):
    consumption_fw = st.number_input("Consumption Freshwater (Ton/Day)", 0)
    price_fw = st.number_input("Price Freshwater (Rp/Ton)", 0)

if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        charter = st.number_input("Angsuran (Rp/Month)", 0)
        crew = st.number_input("Crew (Rp/Month)", 0)
        insurance = st.number_input("Insurance (Rp/Month)", 0)
        docking = st.number_input("Docking (Rp/Month)", 0)
        maintenance = st.number_input("Maintenance (Rp/Month)", 0)
        certificate = st.number_input("Certificate (Rp/Month)", 0)
        premi_nm = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)
else:
    with st.sidebar.expander("🏗️ Charter Cost"):
        charter = st.number_input("Charter Hire (Rp/Month)", 0)
        premi_nm = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)

with st.sidebar.expander("⚓ Port Cost"):
    port_cost_pol = st.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.number_input("Port Cost POD (Rp)", 0)
    asist_tug = st.number_input("Asist Tug (Rp)", 0)

with st.sidebar.expander("🕓 Port Stay"):
    port_stay_pol = st.number_input("POL (Days)", 0)
    port_stay_pod = st.number_input("POD (Days)", 0)

# ===== ADDITIONAL COST =====
with st.sidebar.expander("➕ Additional Cost"):
    if "additional_costs" not in st.session_state:
        st.session_state.additional_costs = []

    add_new = st.button("➕ Add Additional Cost")
    if add_new:
        st.session_state.additional_costs.append({
            "name": "",
            "price": 0,
            "unit": "Ltr",
            "subtype": "Day",
            "consumption": 0
        })

    updated_costs = []
    unit_options = ["Ltr", "Ton", "Month", "Voyage", "MT", "M3", "Day"]

    for i, cost in enumerate(st.session_state.additional_costs):
        st.markdown(f"**Additional Cost {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"Name {i+1}", cost.get("name", ""), key=f"name_{i}")
            price = st.number_input(f"Price {i+1} (Rp)", cost.get("price", 0), key=f"price_{i}")
        with col2:
            unit = st.selectbox(
                f"Unit {i+1}",
                unit_options,
                index=unit_options.index(cost.get("unit", "Ltr")) if cost.get("unit", "Ltr") in unit_options else 0,
                key=f"unit_{i}"
            )
            subtype = "Day"
            if unit in ["Ltr", "Ton"]:
                subtype = st.selectbox(
                    f"Type {i+1}",
                    ["Day", "Hour"],
                    index=["Day", "Hour"].index(cost.get("subtype", "Day")),
                    key=f"subtype_{i}"
                )
            consumption = 0
            if unit in ["Ltr", "Ton"]:
                consumption = st.number_input(
                    f"Consumption {i+1} ({unit}/{subtype})",
                    cost.get("consumption", 0),
                    key=f"consumption_{i}"
                )
        remove = st.button(f"❌ Remove {i+1}", key=f"remove_{i}")
        if not remove:
            updated_costs.append({
                "name": name,
                "price": price,
                "unit": unit,
                "subtype": subtype,
                "consumption": consumption
            })
    st.session_state.additional_costs = updated_costs

# ===== MAIN INPUT =====
st.title("🚢 Freight Calculator Barge")

col1, col2, col3 = st.columns(3)
with col1:
    port_pol = st.text_input("Port Of Loading")
with col2:
    port_pod = st.text_input("Port Of Discharge")
with col3:
    next_port = st.text_input("Next Port")

type_cargo = st.selectbox("Type Cargo", ["Bauxite (MT)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)"])
qyt_cargo = st.number_input("Cargo Quantity", 0.0)
distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0)
distance_pod_pol = st.number_input("Distance POD - POL (NM)", 0.0)
freight_price_input = st.number_input("Freight Price (Rp/MT)", 0)

# ===== PERHITUNGAN =====
if st.button("Calculate Freight 💸"):
    try:
        # Waktu sailing (hour) based on speed inputs (hours)
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        # total voyage in days (sailing hours converted to days + port stays)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_voyage_days_round = int(total_voyage_days) if total_voyage_days % 1 < 0.5 else int(total_voyage_days) + 1

        # consumptions
        total_consumption_fuel = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * total_voyage_days_round
        cost_fw = total_consumption_fw * price_fw
        cost_fuel = total_consumption_fuel * price_fuel

        # core costs
        charter_cost = (charter / 30) * total_voyage_days
        crew_cost = (crew / 30) * total_voyage_days if mode == "Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode == "Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode == "Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode == "Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode == "Owner" else 0
        premi_cost = distance_pol_pod * premi_nm
        port_cost = port_cost_pol + port_cost_pod + asist_tug

        # ===== ADDITIONAL COST CALCULATION =====
        additional_total = 0
        additional_breakdown = {}

        for cost in st.session_state.get("additional_costs", []):
            name = cost.get("name", "")
            unit = cost.get("unit", "")
            subtype = cost.get("subtype", "Day")
            price = cost.get("price", 0)
            cons = cost.get("consumption", 0)

            val = 0
            # Ltr: bisa per Day atau per Hour (Hour uses total_voyage_days * 24)
            if unit == "Ltr":
                if subtype == "Day":
                    val = cons * total_voyage_days * price
                elif subtype == "Hour":
                    val = cons * (total_voyage_days * 24) * price
            # Ton: per Day atau per Hour (Hour uses total_voyage_days * 24)
            elif unit == "Ton":
                if subtype == "Day":
                    val = cons * total_voyage_days * price
                elif subtype == "Hour":
                    val = cons * (total_voyage_days * 24) * price
            # Month: dibagi 30 lalu dikali total_voyage_days
            elif unit == "Month":
                val = (price / 30) * total_voyage_days
            # Voyage: flat per voyage
            elif unit == "Voyage":
                val = price
            # MT / M3: dikalikan total cargo
            elif unit in ["MT", "M3"]:
                val = price * qyt_cargo
            # Day: baru — flat per day (harga x total_voyage_days)
            elif unit == "Day":
                val = price * total_voyage_days

            # kalau nilai > 0, masukkan ke breakdown
            if val and val > 0:
                key_name = name if name else f"{unit} cost"
                # jika nama sama, tambahkan nilainya
                if key_name in additional_breakdown:
                    additional_breakdown[key_name] += val
                else:
                    additional_breakdown[key_name] = val
                additional_total += val

        # ===== TOTAL COST FINAL =====
        total_cost = sum([
            charter_cost, crew_cost, insurance_cost, docking_cost, maintenance_cost, certificate_cost,
            premi_cost, port_cost, cost_fuel, cost_fw, other_cost, additional_total
        ])

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # ===== REVENUE CALC =====
        revenue_user = freight_price_input * qyt_cargo
        pph_user = revenue_user * 0.012
        profit_user = revenue_user - total_cost - pph_user
        profit_percent_user = (profit_user / total_cost * 100) if total_cost > 0 else 0

        # ===== DISPLAY RESULTS =====
        st.subheader("📋 Calculation Results")
        st.markdown(f""" 
        **Total Voyage (Days):** {total_voyage_days:.2f}  
        **Total Sailing Time (Hour):** {sailing_time:.2f}  
        **Total Consumption Fuel (Ltr):** {total_consumption_fuel:,.0f}  
        **Total Consumption Freshwater (Ton):** {total_consumption_fw:,.0f}  
        **Fuel Cost (Rp):** Rp {cost_fuel:,.0f}  
        **Freshwater Cost (Rp):** Rp {cost_fw:,.0f}
        """)

        if mode == "Owner":
            st.markdown("### 🏗️ Owner Costs Summary")
            owner_data = {
                "Angsuran": charter_cost,
                "Crew": crew_cost,
                "Insurance": insurance_cost,
                "Docking": docking_cost,
                "Maintenance": maintenance_cost,
                "Certificate": certificate_cost,
                "Premi": premi_cost,
                "Port Costs": port_cost,
                "Other Costs": other_cost
            }
        else:
            st.markdown("### 🏗️ Charter Costs Summary")
            owner_data = {
                "Charter Hire": charter_cost,
                "Premi": premi_cost,
                "Port Costs": port_cost,
                "Other Costs": other_cost
            }

        for k, v in owner_data.items():
            st.markdown(f"- {k}: Rp {v:,.0f}")

        if additional_breakdown:
            st.markdown("### ➕ Additional Costs")
            for k, v in additional_breakdown.items():
                st.markdown(f"- {k}: Rp {v:,.0f}")

        st.markdown(f"**🧮 Total Cost:** Rp {total_cost:,.0f}")
        st.markdown(f"**🧮 Freight Cost ({type_cargo.split()[1]}):** Rp {freight_cost_mt:,.0f}")

        # ===== FREIGHT PRICE CALCULATION USER (Conditional) =====
        st.subheader("💰 Freight Price Calculation User")
        if freight_price_input > 0:
            st.markdown(f"""
            **Freight Price (Rp/MT):** Rp {freight_price_input:,.0f}  
            **Revenue:** Rp {revenue_user:,.0f}  
            **PPH 1.2%:** Rp {pph_user:,.0f}  
            **Profit:** Rp {profit_user:,.0f}  
            **Profit %:** {profit_percent_user:.2f} %
            """)
        else:
            st.info("Masukkan Freight Price untuk melihat hasil perhitungan profit user.")

        # ===== PROFIT SCENARIO =====
        data = []
        for p in range(0, 80, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"Rp {freight_persen:,.0f}", f"Rp {revenue:,.0f}", f"Rp {pph:,.0f}", f"Rp {profit:,.0f}"])
        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])

        st.subheader("💹 Profit Scenario 0–75%")
        st.dataframe(df_profit, use_container_width=True)

                # ===== PDF GENERATOR =====
        def create_pdf(username):
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=20,
                leftMargin=20,
                topMargin=25,
                bottomMargin=25
            )

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='HeaderBlue', fontSize=18, textColor=colors.HexColor("#0d47a1"), alignment=1, spaceAfter=4))
            styles.add(ParagraphStyle(name='SubHeader', fontSize=11, textColor=colors.HexColor("#0d47a1"), spaceAfter=6, fontName='Helvetica-Bold'))
            styles.add(ParagraphStyle(name='NormalSmall', fontSize=9, leading=11))
            styles.add(ParagraphStyle(name='Bold', fontSize=9, fontName='Helvetica-Bold'))

            elements = []

            # ===== HEADER =====
            logo_path = "icon-512x512.png"
            logo = Image(logo_path, width=2.5*cm, height=2.5*cm)

            title = Paragraph("<b>Freight Calculation Report</b>", styles['HeaderBlue'])
            header_table = Table([[logo, title]], colWidths=[4*cm, 12*cm])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(header_table)
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", styles['NormalSmall']))
            elements.append(Spacer(1, 10))

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
            t_voyage = Table(voyage_data, colWidths=[8*cm, 8*cm])
            t_voyage.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            elements += [t_voyage, Spacer(1, 10)]

            # ===== OPERATIONAL COST =====
            elements.append(Paragraph("Operational & Cost Summary", styles['SubHeader']))
            calc_data = [
                ["Total Sailing Time (Hour)", f"{sailing_time:.2f}"],
                ["Total Consumption Fuel (Ltr)", f"{total_consumption_fuel:,.0f}"],
                ["Total Consumption Freshwater (Ton)", f"{total_consumption_fw:,.0f}"],
                ["Fuel Cost (Rp)", f"Rp {cost_fuel:,.0f}"],
                ["Freshwater Cost (Rp)", f"Rp {cost_fw:,.0f}"],
            ]

            for k, v in owner_data.items():
                calc_data.append([k, f"Rp {v:,.0f}"])

            if additional_breakdown:
                calc_data.append(["--- Additional Costs ---", ""])
                for k, v in additional_breakdown.items():
                    calc_data.append([k, f"Rp {v:,.0f}"])

            calc_data.append(["Total Cost (Rp)", f"Rp {total_cost:,.0f}"])
            calc_data.append([f"Freight Cost ({type_cargo.split()[1]})", f"Rp {freight_cost_mt:,.0f}"])

            t_calc = Table(calc_data, colWidths=[8*cm, 8*cm])
            t_calc.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            elements += [t_calc, Spacer(1, 10)]

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
                t_fpc = Table(fpc_data, colWidths=[8*cm, 8*cm])
                t_fpc.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                elements += [t_fpc, Spacer(1, 10)]

            # ===== PROFIT SCENARIO =====
            elements.append(Paragraph("Profit Scenario 0–75%", styles['SubHeader']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t_profit = Table(profit_table, colWidths=[60, 90, 90, 90, 90])
            t_profit.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            elements += [t_profit, Spacer(1, 10)]

            # ===== FOOTER =====
            footer_text = f"Generated by {username} | https://freight-calculator-barge-byiqna.streamlit.app/"
            elements.append(Paragraph(footer_text, styles['NormalSmall']))

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

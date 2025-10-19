# ============================================
# 📋 Freight Calculator (Clean Version)
# ============================================

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Freight Calculator", page_icon="💰", layout="wide")

# --------------------------------------------
# INPUT SECTION
# --------------------------------------------
st.title("💰 Freight Price Calculation")

col1, col2, col3 = st.columns(3)
with col1:
    port_pol = st.text_input("Port of Loading")
with col2:
    port_pod = st.text_input("Port of Discharge")
with col3:
    next_port = st.text_input("Next Port")

type_cargo = st.selectbox("Type of Cargo", ["Coal (MT)", "Cement (MT)", "Sand (MT)", "Other"])
cargo_qty = st.number_input("Cargo Quantity (MT)", min_value=0.0, step=100.0)
distance_nm = st.number_input("Distance (NM)", min_value=0.0, step=10.0)

fuel_price = st.number_input("Fuel Price (Rp/Liter)", min_value=0.0, value=13500.0, step=100.0)
freshwater_price = st.number_input("Freshwater Price (Rp/Ton)", min_value=0.0, value=120000.0, step=5000.0)

freight_price_input = st.number_input("Freight Price Input (Rp)", min_value=0.0, step=100000.0)

# --------------------------------------------
# CALCULATION SECTION
# --------------------------------------------
total_voyage_days = round(distance_nm / 19.75, 2) if distance_nm else 0
total_sailing_hours = round(total_voyage_days * 11.52, 2)
total_fuel_consumption = round(distance_nm * 73.15, 2)
total_freshwater = round(total_voyage_days * 2, 2)

fuel_cost = total_fuel_consumption * fuel_price
freshwater_cost = total_freshwater * freshwater_price

# --------------------------------------------
# DISPLAY CALCULATION RESULTS
# --------------------------------------------
st.markdown("### 📋 Calculation Results")

calculation_data = {
    "Port Of Loading": port_pol,
    "Port Of Discharge": port_pod,
    "Next Port": next_port,
    "Type Cargo": type_cargo,
    "Cargo Quantity (MT)": f"{cargo_qty:,.0f}" if cargo_qty else "-",
    "Distance (NM)": f"{distance_nm:,.0f}" if distance_nm else "-",
    "Total Voyage (Days)": f"{total_voyage_days:,.2f}",
    "Total Sailing Time (Hour)": f"{total_sailing_hours:,.2f}",
    "Total Consumption Fuel (Ltr)": f"{total_fuel_consumption:,.0f}",
    "Total Consumption Freshwater (Ton)": f"{total_freshwater:,.0f}",
    "Fuel Cost (Rp)": f"Rp {fuel_cost:,.0f}",
    "Freshwater Cost (Rp)": f"Rp {freshwater_cost:,.0f}"
}

for key, value in calculation_data.items():
    st.markdown(f"- **{key}:** {value}")

# --------------------------------------------
# OWNER COSTS SUMMARY
# --------------------------------------------
st.markdown("### 🏗️ Owner Costs Summary")
owner_data = {
    "Angsuran": 250000000,
    "Crew": 150000000,
    "Insurance": 50000000,
    "Docking": 80000000,
    "Maintenance": 70000000,
    "Certificate": 20000000,
    "Premi": 15000000,
    "Port Costs": 30000000,
    "Other Costs": 25000000,
}

for key, value in owner_data.items():
    st.markdown(f"- **{key}:** Rp {value:,.0f}")

# --------------------------------------------
# FREIGHT PRICE INPUT (OPTIONAL)
# --------------------------------------------
if freight_price_input > 0:
    st.markdown("### 💵 Freight Price Calculation User")
    st.markdown(f"- Freight Price Input: Rp {freight_price_input:,.0f}")

    scenario_50 = freight_price_input * 0.5
    scenario_100 = freight_price_input
    st.markdown("#### 📈 Profit Scenario")
    st.markdown(f"- 50% Scenario: Rp {scenario_50:,.0f}")
    st.markdown(f"- 100% Scenario: Rp {scenario_100:,.0f}")

# --------------------------------------------
# GENERATE PDF REPORT
# --------------------------------------------
try:
    def create_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("<b>Freight Price Calculation Report</b>", styles['Title']))
        elements.append(Spacer(1, 12))

        # Calculation Results
        elements.append(Paragraph("<b>📋 Calculation Results</b>", styles['Heading3']))
        for key, value in calculation_data.items():
            elements.append(Paragraph(f"- {key}: {value}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Owner Cost Summary
        elements.append(Paragraph("<b>🏗️ Owner Costs Summary</b>", styles['Heading3']))
        for key, value in owner_data.items():
            elements.append(Paragraph(f"- {key}: Rp {value:,.0f}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Freight Price Section
        if freight_price_input > 0:
            elements.append(Paragraph("<b>💵 Freight Price Calculation User</b>", styles['Heading3']))
            elements.append(Paragraph(f"- Freight Price Input: Rp {freight_price_input:,.0f}", styles['Normal']))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("<b>📈 Profit Scenario</b>", styles['Heading3']))
            elements.append(Paragraph(f"- 50% Scenario: Rp {scenario_50:,.0f}", styles['Normal']))
            elements.append(Paragraph(f"- 100% Scenario: Rp {scenario_100:,.0f}", styles['Normal']))
            elements.append(Spacer(1, 12))

        # Footer
        elements.append(Paragraph("<i>Generated By: https://freight-calculatordemo2.streamlit.app/</i>", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    pdf_buffer = create_pdf()
    file_name = f"Freight_Report_{port_pol}_{port_pod}_{datetime.now():%Y%m%d}.pdf"

    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_buffer,
        file_name=file_name,
        mime="application/pdf"
    )

except Exception as e:
    st.error(f"Error: {e}")

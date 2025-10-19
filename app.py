import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

st.set_page_config(page_title="Freight Calculator", layout="wide")

st.title("⛴️ Freight Calculator")

try:
    # ===== INPUT SECTION =====
    st.header("📥 Input Data")

    col1, col2 = st.columns(2)
    with col1:
        port_pol = st.text_input("Port Of Loading")
        port_pod = st.text_input("Port Of Discharge")
        next_port = st.text_input("Next Port")
        type_cargo = st.selectbox("Type Cargo", ["Coal (MT)", "Iron Ore (MT)", "Cement (MT)"])
        distance_nm = st.number_input("Distance (NM)", min_value=0.0, value=380.0)
        qyt_cargo = st.number_input("Cargo Quantity (MT)", min_value=0.0, value=7500.0)
    with col2:
        total_voyage_days = st.number_input("Total Voyage (Days)", min_value=0.0, value=19.24)
        total_sailing_time = st.number_input("Total Sailing Time (Hour)", min_value=0.0, value=221.67)
        total_fuel_consumption = st.number_input("Total Consumption Fuel (Ltr)", min_value=0.0, value=27800.0)
        total_fw_consumption = st.number_input("Total Consumption Freshwater (Ton)", min_value=0.0, value=38.0)
        fuel_cost = st.number_input("Fuel Cost (Rp)", min_value=0.0, value=375300000.0)
        fw_cost = st.number_input("Freshwater Cost (Rp)", min_value=0.0, value=4560000.0)
        freight_price_input = st.number_input("Freight Price (Rp/MT)", min_value=0.0, value=0.0)

    # ===== OWNER COSTS =====
    st.markdown("### 🏗️ Owner Costs Summary")
    owner_data = {
        "Angsuran": 120000000,
        "Crew": 80000000,
        "Insurance": 20000000,
        "Docking": 15000000,
        "Maintenance": 10000000,
        "Certificate": 5000000,
        "Premi": 3000000,
        "Port Costs": 12000000,
        "Other Costs": 5000000
    }

    for k, v in owner_data.items():
        st.markdown(f"- **{k}:** Rp {v:,.0f}")

    total_cost = sum(owner_data.values()) + fuel_cost + fw_cost
    freight_cost_mt = total_cost / qyt_cargo

    st.markdown(f"**🧮 Total Cost:** Rp {total_cost:,.0f}")
    st.markdown(f"**🧮 Freight Cost ({type_cargo.split()[1]}):** Rp {freight_cost_mt:,.0f}")

    # ===== CALCULATION RESULTS (VERTIKAL RAPIH) =====
    st.markdown("### 📋 Calculation Results")
    st.markdown("---")

    calc_results = {
        "Port Of Loading": port_pol,
        "Port Of Discharge": port_pod,
        "Next Port": next_port,
        "Type Cargo": type_cargo,
        "Cargo Quantity (MT)": f"{qyt_cargo:,.0f}",
        "Distance (NM)": f"{distance_nm:,.0f}",
        "Total Voyage (Days)": f"{total_voyage_days:.2f}",
        "Total Sailing Time (Hour)": f"{total_sailing_time:.2f}",
        "Total Consumption Fuel (Ltr)": f"{total_fuel_consumption:,.0f}",
        "Total Consumption Freshwater (Ton)": f"{total_fw_consumption:,.0f}",
        "Fuel Cost (Rp)": f"Rp {fuel_cost:,.0f}",
        "Freshwater Cost (Rp)": f"Rp {fw_cost:,.0f}"
    }

    for k, v in calc_results.items():
        st.markdown(f"**{k}:** {v}")

    st.markdown("---")

    # ===== FREIGHT PRICE CALCULATION USER =====
    if freight_price_input > 0:
        revenue_user = freight_price_input * qyt_cargo
        pph_user = revenue_user * 0.012
        profit_user = revenue_user - total_cost - pph_user
        profit_percent_user = (profit_user / total_cost) * 100

        st.subheader("💰 Freight Price Calculation User")
        st.markdown(f"""
**Freight Price (Rp/MT):** Rp {freight_price_input:,.0f}  
**Revenue:** Rp {revenue_user:,.0f}  
**PPH 1.2%:** Rp {pph_user:,.0f}  
**Profit:** Rp {profit_user:,.0f}  
**Profit %:** {profit_percent_user:.2f} %
""")

    # ===== PROFIT SCENARIO 0–50% =====
    data = []
    for p in range(0, 55, 5):
        freight_persen = freight_cost_mt * (1 + p / 100)
        revenue = freight_persen * qyt_cargo
        pph = revenue * 0.012
        profit = revenue - total_cost - pph
        data.append([f"{p}%", f"Rp {freight_persen:,.0f}", f"Rp {revenue:,.0f}", f"Rp {pph:,.0f}", f"Rp {profit:,.0f}"])

    df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
    st.subheader("💹 Profit Scenario 0-50%")
    st.dataframe(df_profit, use_container_width=True)

    # ===== PDF GENERATOR =====
    def create_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("<b>Freight Calculator Report</b>", styles['Title']))
        elements.append(Spacer(1, 12))

        # Voyage Information
        elements.append(Paragraph("<b>Voyage Information</b>", styles['Heading3']))
        voyage_data = [[k, v] for k, v in calc_results.items()]
        t_voyage = Table(voyage_data, hAlign='LEFT', colWidths=[180, 200])
        t_voyage.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(t_voyage)
        elements.append(Spacer(1, 12))

        # Owner Cost Summary
        elements.append(Paragraph("<b>Owner Costs Summary</b>", styles['Heading3']))
        owner_table = [[k, f"Rp {v:,.0f}"] for k, v in owner_data.items()]
        t_owner = Table(owner_table, hAlign='LEFT', colWidths=[180, 200])
        t_owner.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(t_owner)
        elements.append(Spacer(1, 12))

        # Freight Price Calculation (conditional)
        if freight_price_input > 0:
            elements.append(Paragraph("<b>Freight Price Calculation User</b>", styles['Heading3']))
            fpc_data = [
                ["Freight Price (Rp/MT)", f"Rp {freight_price_input:,.0f}"],
                ["Revenue", f"Rp {revenue_user:,.0f}"],
                ["PPH 1.2%", f"Rp {pph_user:,.0f}"],
                ["Profit", f"Rp {profit_user:,.0f}"],
                ["Profit %", f"{profit_percent_user:.2f} %"]
            ]
            t_fpc = Table(fpc_data, hAlign='LEFT', colWidths=[180, 200])
            t_fpc.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
            elements.append(t_fpc)
            elements.append(Spacer(1, 12))

        # Profit Scenario
        elements.append(Paragraph("<b>Profit Scenario 0-50%</b>", styles['Heading3']))
        profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
        t_profit = Table(profit_table, hAlign='LEFT', colWidths=[70, 100, 100, 100, 100])
        t_profit.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(t_profit)
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

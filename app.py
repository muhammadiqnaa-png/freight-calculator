import streamlit as st
# Profit Scenario
# ==============================
st.subheader("📈 Freight dengan Profit (0% - 50%)")
profit_list = []
for p in range(0, 55, 5):
freight = cost_per_mt * (1 + (p / 100))
revenue = freight * total_cargo
Pph = revenue * 0.012
net_profit = revenue - Pph - total_cost
profit_list.append([f"{p}%", f"Rp {freight:,.0f}", f"Rp {revenue:,.0f}", f"Rp {Pph:,.0f}", f"Rp {net_profit:,.0f}"])
profit_df = pd.DataFrame(profit_list, columns=["Profit %", "Freight / MT", "Revenue", "Pph", "Net Profit"])
st.table(profit_df)


# ==============================
# PDF Report
# ==============================
input_data = [
["POL", pol],
["POD", pod],
["Jarak (NM)", f"{jarak:,}"],
["Total Cargo (MT)", f"{total_cargo:,}"],
["Voyage Days", f"{voyage_days:,.2f} hari"],
]
results = list(biaya_mode_rp.items()) + list(biaya_umum_rp.items())
results.append(["TOTAL COST", f"Rp {total_cost:,.0f}"])
results.append(["Cost per MT", f"Rp {cost_per_mt:,.0f} / MT"])


def generate_pdf(input_data, results, profit_df):
buffer = BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4,
leftMargin=60, rightMargin=50, topMargin=30, bottomMargin=40
)
elements = []
styles = getSampleStyleSheet()
elements.append(Paragraph("🚢 Laporan Freight Tongkang", styles["Title"]))
elements.append(Paragraph("📥 Input Utama", styles["Heading2"]))
table_input = Table(input_data, colWidths=[200, 200])
table_input.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey), ("FONTSIZE", (0,0), (-1,-1), 9)]))
elements.append(table_input)
elements.append(Spacer(1,1))


elements.append(Paragraph("📊 Hasil Perhitungan", styles["Heading2"]))
table_results = Table(results, colWidths=[200, 200])
table_results.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey), ("FONTSIZE", (0,0), (-1,-1), 9)]))
elements.append(table_results)
elements.append(Spacer(1,1))


elements.append(Paragraph("📈 Skenario Profit (0% - 50%)", styles["Heading2"]))
data_profit = [list(profit_df.columns)] + profit_df.values.tolist()
table_profit = Table(data_profit, colWidths=[60,100,120,120,120])
table_profit.setStyle(TableStyle([
("GRID", (0,0), (-1,-1), 0.5, colors.grey),
("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
("ALIGN", (1,1), (-1,-1), "RIGHT"),
("ALIGN", (0,1), (0,-1), "LEFT"),
("FONTSIZE", (0,0), (-1,-1), 9)
]))
elements.append(table_profit)
doc.build(elements)
buffer.seek(0)
return buffer


pdf_buffer = generate_pdf(input_data, results, profit_df)


st.download_button(
label="📥 Download Laporan PDF",
data=pdf_buffer,
file_name=f"Freight_Report_{pol or 'POL'}_{pod or 'POD'}.pdf",
mime="application/pdf"
)


# ==============================
# Logout
# ==============================
st.sidebar.markdown("---")
logout_btn = st.sidebar.button("Logout")
if logout_btn:
st.session_state.logged_in = False
st.session_state.username = ""
st.experimental_rerun()

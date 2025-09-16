import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Freight Calculator", layout="wide")

st.title("🚢 Freight Calculator Tongkang")

# ==============================
# Default Parameter (editable)
# ==============================
st.sidebar.header("⚙️ Parameter Default (Bisa diubah)")

speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=4.0)
consumption = st.sidebar.number_input("Consumption (liter/jam)", value=120)
harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=12500)
harga_air_tawar = st.sidebar.number_input("Harga Air Tawar (Rp/Ton)", value=120000)
charter_hire = st.sidebar.number_input("Charter hire/bulan (Rp)", value=750000000)
crew_cost = st.sidebar.number_input("Crew cost/bulan (Rp)", value=60000000)
asuransi = st.sidebar.number_input("Asuransi/bulan (Rp)", value=50000000)
docking = st.sidebar.number_input("Docking Saving/bulan (Rp)", value=50000000)
perawatan = st.sidebar.number_input("Perawatan Fleet/bulan (Rp)", value=50000000)
Sertifikat = st.sidebar.number_input("Sertifikat/bulan (Rp)", value=50000000)
port_cost = st.sidebar.number_input("Port cost/call (Rp)", value=50000000)
asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=35000000)
premi_nm = st.sidebar.number_input("Premi (Rp/NM)", value=50000)
Depresiasi = st.sidebar.number_input("Depresiasi (Rp/Beli)", value=45000000000)
Other_Cost = st.sidebar.number_input("Other Cost (Rp)", value=50000000)
port_stay = st.sidebar.number_input("Port Stay (Hari)", value=10)

# ==============================
# Input Utama dari User
# ==============================
st.header("📥 Input Utama")
pol = st.text_input("Port of Loading (POL)", value="")
pod = st.text_input("Port of Discharge (POD)", value="")
total_cargo = st.number_input("Total Cargo (MT)", value=7500)
jarak = st.number_input("Jarak (NM)", value=630)

# ==============================
# Perhitungan
# ==============================
sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)
voyage_days = (sailing_time / 24) + port_stay
total_consumption = (sailing_time * consumption) + (port_stay * consumption)

biaya_charter = (charter_hire / 30) * voyage_days
biaya_bunker = total_consumption * harga_bunker
biaya_air_tawar = (voyage_days * 2) * harga_air_tawar
biaya_crew = (crew_cost / 30) * voyage_days
biaya_port = port_cost * 2
premi_cost = premi_nm * jarak
biaya_asist = asist_tug
other_cost = ((asuransi / 30) * voyage_days) + ((docking / 30) * voyage_days) + ((perawatan / 30) * voyage_days) + ((Sertifikat / 30) * voyage_days) + (Other_Cost) + (((Depresiasi / 15) / 12 / 30) * voyage_days)

total_cost = biaya_charter + biaya_bunker + biaya_air_tawar + biaya_crew + biaya_port + premi_cost + biaya_asist + other_cost
cost_per_mt = total_cost / total_cargo

# ==============================
# Tampilkan Hasil
# ==============================
st.header("📊 Hasil Perhitungan")

st.write(f"**Sailing Time (jam):** {sailing_time:,.2f}")
st.write(f"**Total Voyage Days:** {voyage_days:,.2f}")
st.write(f"**Total Consumption (liter):** {total_consumption:,.0f}")

st.subheader("💰 Biaya Detail")
st.write(f"- Biaya Charter: Rp {biaya_charter:,.0f}")
st.write(f"- Biaya Bunker: Rp {biaya_bunker:,.0f}")
st.write(f"- Biaya air tawar : Rp {biaya_air_tawar:,.0f}")
st.write(f"- Biaya Crew: Rp {biaya_crew:,.0f}")
st.write(f"- Biaya Port: Rp {biaya_port:,.0f}")
st.write(f"- Premi Cost: Rp {premi_cost:,.0f}")
st.write(f"- Asist Tug: Rp {biaya_asist:,.0f}")
st.write(f"- Other Cost: Rp {other_cost:,.0f}")
st.write(f"**Total Cost: Rp {total_cost:,.0f}**")

st.subheader("📦 Cost per MT")
st.write(f"Rp {cost_per_mt:,.0f} / MT")

# ==============================
# Profit Scenario 0% - 50%
# ==============================
st.subheader("📈 Freight dengan Profit (0% - 50%)")

profit_list = []
for p in range(0, 55, 5):
    freight = cost_per_mt * (1 + (p/100))
    profit_list.append([f"{p}%", f"Rp {freight:,.0f}"])

df = pd.DataFrame(profit_list, columns=["Profit", "Freight per MT"])
st.table(df)

# ==============================
# Kumpulan Data untuk PDF
# ==============================
input_data = [
    ["Port of Loading (POL)", pol],
    ["Port of Discharge (POD)", pod],
    ["Jarak (NM)", f"{jarak:,}"],
    ["Total Cargo (MT)", f"{total_cargo:,}"],
]

results = [
    ["Sailing Time (jam)", f"{sailing_time:,.2f}"],
    ["Total Voyage Days", f"{voyage_days:,.2f}"],
    ["Total Consumption (liter)", f"{total_consumption:,.0f}"],
    ["Biaya Charter", f"Rp {biaya_charter:,.0f}"],
    ["Biaya Bunker", f"Rp {biaya_bunker:,.0f}"],
    ["Biaya Air Tawar", f"Rp {biaya_air_tawar:,.0f}"],
    ["Biaya Crew", f"Rp {biaya_crew:,.0f}"],
    ["Biaya Port", f"Rp {biaya_port:,.0f}"],
    ["Premi Cost", f"Rp {premi_cost:,.0f}"],
    ["Asist Tug", f"Rp {biaya_asist:,.0f}"],
    ["Other Cost", f"Rp {other_cost:,.0f}"],
    ["TOTAL COST", f"Rp {total_cost:,.0f}"],
    ["Cost per MT", f"Rp {cost_per_mt:,.0f} / MT"],
]

profit_list = []
for p in range(0, 55, 5):
    freight = cost_per_mt * (1 + (p/100))
    revenue = freight * total_cargo
    net_profit = revenue - total_cost
    profit_list.append([f"{p}%", f"Rp {freight:,.0f}", f"Rp {revenue:,.0f}", f"Rp {net_profit:,.0f}"])

profit_df = pd.DataFrame(profit_list, columns=["Profit %", "Freight / MT", "Revenue", "Net Profit"])

# ==============================
# Fungsi Generate PDF
# ==============================
def generate_pdf(input_data, results, profit_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Judul
    elements.append(Paragraph("🚢 Freight Report Tongkang", styles["Title"]))

    # Input Utama
    elements.append(Paragraph("📥 Input Utama", styles["Heading2"]))
    table_input = Table(input_data, colWidths=[200, 200])
    table_input.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.whitesmoke),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
    ]))
    elements.append(table_input)
    elements.append(Spacer(1, 12))

    # Hasil Perhitungan & Biaya
    elements.append(Paragraph("📊 Hasil Perhitungan & Biaya", styles["Heading2"]))
    table_results = Table(results, colWidths=[200, 200])
    table_results.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.whitesmoke),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
    ]))
    elements.append(table_results)
    elements.append(Spacer(1, 12))

    # Profit Scenario
    elements.append(Paragraph("📈 Profit Scenario (0% - 50%)", styles["Heading2"]))
    data_profit = [list(profit_df.columns)] + profit_df.values.tolist()
    table_profit = Table(data_profit, colWidths=[60, 100, 120, 120])
    table_profit.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ]))
    elements.append(table_profit)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==============================
# Tombol Download PDF
# ==============================
pdf_buffer = generate_pdf(input_data, results, profit_df)

st.download_button(
    label="📥 Download Laporan PDF",
    data=pdf_buffer,
    file_name=f"Freight_Report_{pol}_{pod}.pdf",
    mime="application/pdf"
)

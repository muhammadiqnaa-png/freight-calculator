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
# Pilihan Mode di Depan
# ==============================
st.header("💼 Pilih Mode Biaya")
mode = st.radio("Owner atau Charter?", ["Owner", "Charter"])

# ==============================
# Input Utama Kapal / Operasional
# ==============================
st.header("📥 Input Utama")
pol = st.text_input("Port of Loading (POL)")
pod = st.text_input("Port of Discharge (POD)")
total_cargo = st.number_input("Total Cargo (MT)", value=7500)
jarak = st.number_input("Jarak (NM)", value=630)
port_stay = st.number_input("Port Stay (Hari)", value=10)

# ==============================
# Parameter Default
# ==============================
speed_kosong = st.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.number_input("Speed Isi (knot)", value=4.0)
consumption = st.number_input("Consumption (liter/jam)", value=120)
harga_bunker = st.number_input("Harga Bunker (Rp/liter)", value=12500)
harga_air_tawar = st.number_input("Harga Air Tawar (Rp/Ton)", value=120000)
charter_hire = st.number_input("Charter hire/bulan (Rp)", value=750_000_000)
crew_cost = st.number_input("Crew cost/bulan (Rp)", value=60_000_000)
asuransi = st.number_input("Asuransi/bulan (Rp)", value=50_000_000)
docking = st.number_input("Docking Saving/bulan (Rp)", value=50_000_000)
perawatan = st.number_input("Perawatan Fleet/bulan (Rp)", value=50_000_000)
Sertifikat = st.number_input("Sertifikat/bulan (Rp)", value=50_000_000)
port_cost = st.number_input("Port cost/call (Rp)", value=50_000_000)
asist_tug = st.number_input("Asist Tug (Rp)", value=35_000_000)
premi_nm = st.number_input("Premi (Rp/NM)", value=50_000)
Depresiasi = st.number_input("Depresiasi (Rp/Beli)", value=45_000_000_000)
Other_Cost = st.number_input("Other Cost (Rp)", value=50_000_000)

# ==============================
# Perhitungan
# ==============================
sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)
voyage_days = (sailing_time / 24) + port_stay
total_consumption = (sailing_time * consumption) + (port_stay * consumption)

if mode == "Owner":
    biaya_mode = ((crew_cost / 30) * voyage_days + 
                  (asuransi / 30) * voyage_days + 
                  ((docking / 30) * voyage_days) + 
                  ((perawatan / 30) * voyage_days) +
                  ((Sertifikat / 30) * voyage_days) +
                  Other_Cost +
                  (((Depresiasi / 15) / 12 / 30) * voyage_days))
else:
    biaya_mode = (charter_hire / 30) * voyage_days

biaya_bunker = total_consumption * harga_bunker
biaya_air_tawar = (voyage_days * 2) * harga_air_tawar
biaya_port = port_cost * 2
premi_cost = premi_nm * jarak
biaya_asist = asist_tug

total_cost = biaya_mode + biaya_bunker + biaya_air_tawar + biaya_port + premi_cost + biaya_asist
cost_per_mt = total_cost / total_cargo

# ==============================
# Tampilkan Hasil
# ==============================
st.header("📊 Hasil Perhitungan")
st.write(f"**Sailing Time (jam):** {sailing_time:,.2f}")
st.write(f"**Total Voyage Days:** {voyage_days:,.2f}")
st.write(f"**Total Consumption (liter):** {total_consumption:,.0f}")
st.subheader(f"💰 Total Cost ({mode})")
st.write(f"Rp {biaya_mode:,.0f} (Biaya Mode)")
st.write(f"Rp {biaya_bunker:,.0f} (Bunker BBM)")
st.write(f"Rp {biaya_air_tawar:,.0f} (Air Tawar)")
st.write(f"Rp {biaya_port:,.0f} (Port Cost)")
st.write(f"Rp {premi_cost:,.0f} (Premi)")
st.write(f"Rp {biaya_asist:,.0f} (Asist)")
st.write(f"**TOTAL COST: Rp {total_cost:,.0f}**")
st.subheader("📦 Cost per MT")
st.write(f"Rp {cost_per_mt:,.0f} / MT")

# ==============================
# Profit Scenario 0% - 50%
# ==============================
st.subheader("📈 Freight dengan Profit (0% - 50%)")
profit_list = []
for p in range(0, 55, 5):
    freight = cost_per_mt * (1 + (p/100))
    revenue = freight * total_cargo
    net_profit = revenue - total_cost
    profit_list.append([f"{p}%", f"Rp {freight:,.0f}", f"Rp {revenue:,.0f}", f"Rp {net_profit:,.0f}"])
profit_df = pd.DataFrame(profit_list, columns=["Profit %", "Freight / MT", "Revenue", "Net Profit"])
st.table(profit_df)

# ==============================
# PDF
# ==============================
input_data = [
    ["POL", pol],
    ["POD", pod],
    ["Jarak (NM)", f"{jarak:,}"],
    ["Total Cargo (MT)", f"{total_cargo:,}"],
]

results = [
    ["Sailing Time (jam)", f"{sailing_time:,.2f}"],
    ["Total Voyage Days", f"{voyage_days:,.2f}"],
    ["Total Consumption (liter)", f"{total_consumption:,.0f}"],
    ["Biaya Mode", f"Rp {biaya_mode:,.0f}"],
    ["Bunker BBM", f"Rp {biaya_bunker:,.0f}"],
    ["Air Tawar", f"Rp {biaya_air_tawar:,.0f}"],
    ["Port Cost", f"Rp {biaya_port:,.0f}"],
    ["Premi", f"Rp {premi_cost:,.0f}"],
    ["Asist", f"Rp {biaya_asist:,.0f}"],
    ["TOTAL COST", f"Rp {total_cost:,.0f}"],
    ["Cost per MT", f"Rp {cost_per_mt:,.0f} / MT"],
]

def generate_pdf(input_data, results, profit_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("🚢 Freight Report Tongkang", styles["Title"]))
    elements.append(Paragraph("📥 Input Utama", styles["Heading2"]))
    table_input = Table(input_data, colWidths=[200, 200])
    table_input.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                                     ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke)]))
    elements.append(table_input)
    elements.append(Spacer(1,12))

    elements.append(Paragraph("📊 Hasil Perhitungan", styles["Heading2"]))
    table_results = Table(results, colWidths=[200, 200])
    table_results.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                                       ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke)]))
    elements.append(table_results)
    elements.append(Spacer(1,12))

    elements.append(Paragraph("📈 Profit Scenario (0% - 50%)", styles["Heading2"]))
    data_profit = [list(profit_df.columns)] + profit_df.values.tolist()
    table_profit = Table(data_profit, colWidths=[60,100,120,120])
    table_profit.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                                     ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                                     ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                                     ("ALIGN", (1,1), (-1,-1), "RIGHT")]))
    elements.append(table_profit)

    doc.build(elements)
    buffer.seek(0)
    return buffer

st.download_button(
    "📥 Download Laporan PDF",
    data=pdf_buffer,
    file_name=f"Freight_Report_{pol}_{pod}.pdf",
    mime="application/pdf"

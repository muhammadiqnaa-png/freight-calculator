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
# Pilihan Mode Owner / Charter
# ==============================

st.sidebar.header("💼 Mode Biaya")
mode = st.sidebar.radio("Pilih Mode:", ["Owner", "Charter"])
if mode == "Owner":
    st.sidebar.subheader("💰 Biaya Owner")
    angsuran = st.sidebar.number_input("Angsuran (Bulan)", value=0)
    bunker_bbm = st.sidebar.number_input("Bunker BBM (Rp)", value=0)
    bunker_air = st.sidebar.number_input("Bunker Air Tawar (Rp)", value=0)
    crew_cost_owner = st.sidebar.number_input("Crew Cost (Rp)", value=0)
    asuransi_owner = st.sidebar.number_input("Asuransi (Rp)", value=0)
    docking_owner = st.sidebar.number_input("Docking (Rp)", value=0)
    perawatan_owner = st.sidebar.number_input("Perawatan (Rp)", value=0)
    sertifikat_owner = st.sidebar.number_input("Sertifikat (Rp)", value=0)
    port_cost_owner = st.sidebar.number_input("Port Cost (Rp)", value=0)
    premi_owner = st.sidebar.number_input("Premi (Rp)", value=0)
    asist_owner = st.sidebar.number_input("Asist (Rp)", value=0)
    depresiasi_owner = st.sidebar.number_input("Depresiasi (Rp)", value=0)
    other_owner = st.sidebar.number_input("Other (Rp)", value=0)

    total_biaya_mode = (angsuran + bunker_bbm + bunker_air + crew_cost_owner + asuransi_owner +
                        docking_owner + perawatan_owner + sertifikat_owner + port_cost_owner +
                        premi_owner + asist_owner + depresiasi_owner + other_owner)

else:
    st.sidebar.subheader("💰 Biaya Charter")
    charter_hire = st.sidebar.number_input("Charter Hire (Bulan)", value=0)
    bunker_bbm_charter = st.sidebar.number_input("Bunker BBM (Rp)", value=0)
    bunker_air_charter = st.sidebar.number_input("Bunker Air Tawar (Rp)", value=0)
    port_cost_charter = st.sidebar.number_input("Port Cost (Rp)", value=0)
    premi_charter = st.sidebar.number_input("Premi (Rp)", value=0)
    asist_charter = st.sidebar.number_input("Asist (Rp)", value=0)
    other_charter = st.sidebar.number_input("Other (Rp)", value=0)

    total_biaya_mode = (charter_hire + bunker_bbm_charter + bunker_air_charter +
                        port_cost_charter + premi_charter + asist_charter + other_charter)

# ==============================
# Default Parameter (editable)
# ==============================
st.sidebar.header("⚙️ Parameter Default (Bisa diubah)")
speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=4.0)
consumption = st.sidebar.number_input("Consumption (liter/jam)", value=120)
harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=12500)
jarak_default = st.sidebar.number_input("Jarak Default (NM)", value=630)
port_stay_default = st.sidebar.number_input("Port Stay (Hari)", value=10)
total_cargo_default = st.sidebar.number_input("Total Cargo (MT)", value=7500)

# ==============================
# Pilihan Mode Owner / Charter
# ==============================

st.sidebar.header("💼 Mode Biaya")
mode = st.sidebar.radio("Pilih Mode:", ["Owner", "Charter"])
if mode == "Owner":
    st.sidebar.subheader("💰 Biaya Owner")
    angsuran = st.sidebar.number_input("Angsuran (Bulan)", value=0)
    bunker_bbm = st.sidebar.number_input("Bunker BBM (Rp)", value=0)
    bunker_air = st.sidebar.number_input("Bunker Air Tawar (Rp)", value=0)
    crew_cost_owner = st.sidebar.number_input("Crew Cost (Rp)", value=0)
    asuransi_owner = st.sidebar.number_input("Asuransi (Rp)", value=0)
    docking_owner = st.sidebar.number_input("Docking (Rp)", value=0)
    perawatan_owner = st.sidebar.number_input("Perawatan (Rp)", value=0)
    sertifikat_owner = st.sidebar.number_input("Sertifikat (Rp)", value=0)
    port_cost_owner = st.sidebar.number_input("Port Cost (Rp)", value=0)
    premi_owner = st.sidebar.number_input("Premi (Rp)", value=0)
    asist_owner = st.sidebar.number_input("Asist (Rp)", value=0)
    depresiasi_owner = st.sidebar.number_input("Depresiasi (Rp)", value=0)
    other_owner = st.sidebar.number_input("Other (Rp)", value=0)

    total_biaya_mode = (angsuran + bunker_bbm + bunker_air + crew_cost_owner + asuransi_owner +
                        docking_owner + perawatan_owner + sertifikat_owner + port_cost_owner +
                        premi_owner + asist_owner + depresiasi_owner + other_owner)

else:
    st.sidebar.subheader("💰 Biaya Charter")
    charter_hire = st.sidebar.number_input("Charter Hire (Bulan)", value=0)
    bunker_bbm_charter = st.sidebar.number_input("Bunker BBM (Rp)", value=0)
    bunker_air_charter = st.sidebar.number_input("Bunker Air Tawar (Rp)", value=0)
    port_cost_charter = st.sidebar.number_input("Port Cost (Rp)", value=0)
    premi_charter = st.sidebar.number_input("Premi (Rp)", value=0)
    asist_charter = st.sidebar.number_input("Asist (Rp)", value=0)
    other_charter = st.sidebar.number_input("Other (Rp)", value=0)

    total_biaya_mode = (charter_hire + bunker_bbm_charter + bunker_air_charter +
                        port_cost_charter + premi_charter + asist_charter + other_charter)

# ==============================
# Input Utama dari User
# ==============================
st.header("📥 Input Utama")
pol = st.text_input("Port of Loading (POL)", value="")
pod = st.text_input("Port of Discharge (POD)", value="")
total_cargo = st.number_input("Total Cargo (MT)", value=int(total_cargo_default))
jarak = st.number_input("Jarak (NM)", value=int(jarak_default))
port_stay = st.number_input("Port Stay (Hari)", value=int(port_stay_default))

# ==============================
# Perhitungan
# ==============================
sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)
voyage_days = (sailing_time / 24) + port_stay
total_consumption = (sailing_time * consumption) + (port_stay * consumption)
biaya_bunker = total_consumption * harga_bunker

total_cost = total_biaya_mode + biaya_bunker
cost_per_mt = total_cost / total_cargo

# ==============================
# Tampilkan Hasil
# ==============================
st.header("📊 Hasil Perhitungan")
st.write(f"**Sailing Time (jam):** {sailing_time:,.2f}")
st.write(f"**Total Voyage Days:** {voyage_days:,.2f}")
st.write(f"**Total Consumption (liter):** {total_consumption:,.0f}")
st.subheader(f"💰 Total Biaya ({mode})")
st.write(f"Rp {total_biaya_mode:,.0f} (Biaya Mode)")
st.write(f"Rp {biaya_bunker:,.0f} (Bunker BBM)")
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
    ["Total Biaya Mode", f"Rp {total_biaya_mode:,.0f}"],
    ["Bunker BBM", f"Rp {biaya_bunker:,.0f}"],
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

pdf_buffer = generate_pdf(input_data, results, profit_df)
st.download_button("📥 Download Laporan PDF", data=pdf_buffer,
                   file_name=f"Freight_Report_{pol}_{pod}.pdf", mime="application/pdf")

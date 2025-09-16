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
# Pilih Mode
# ==============================
mode = st.radio("Pilih Mode Biaya:", ["Owner", "Charter"])

# ==============================
# Input Utama Kapal / Operasional
# ==============================
st.header("📥 Input Utama")
pol = st.text_input("Port of Loading (POL)")
pod = st.text_input("Port of Discharge (POD)")
total_cargo = st.number_input("Total Cargo (MT)", value=7500)
jarak = st.number_input("Jarak (NM)", value=630)

# ==============================
# Sidebar Parameter (Dinamis sesuai mode)
# ==============================
st.sidebar.header("⚙️ Parameter Default (Bisa diubah)")

# Parameter umum
speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=4.0)
consumption = st.sidebar.number_input("Consumption (liter/jam)", value=120)
harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=12500)
harga_air_tawar = st.sidebar.number_input("Harga Air Tawar (Rp/Ton)", value=120000)
port_cost = st.sidebar.number_input("Port cost/call (Rp)", value=50000000)
asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=35000000)
premi_nm = st.sidebar.number_input("Premi (Rp/NM)", value=50000)

# Parameter khusus per mode
if mode == "Owner":
    angsuran = st.sidebar.number_input("Angsuran (Rp/bulan)", value=750000000)
    crew_cost = st.sidebar.number_input("Crew Cost (Rp/bulan)", value=60000000)
    asuransi = st.sidebar.number_input("Asuransi (Rp/bulan)", value=50000000)
    docking = st.sidebar.number_input("Docking (Rp/bulan)", value=50000000)
    perawatan = st.sidebar.number_input("Perawatan (Rp/bulan)", value=50000000)
    sertifikat = st.sidebar.number_input("Sertifikat (Rp/bulan)", value=50000000)
    depresiasi = st.sidebar.number_input("Depresiasi (Rp/Beli)", value=45000000000)
    other_cost = st.sidebar.number_input("Other Cost (Rp)", value=50000000)
else:  # Charter
    charter_hire = st.sidebar.number_input("Charter Hire (Rp/bulan)", value=750000000)
    other_cost = st.sidebar.number_input("Other Cost (Rp)", value=50000000)

# Port Stay paling bawah
port_stay = st.sidebar.number_input("Port Stay (Hari)", value=10)

# ==============================
# Perhitungan Dasar
# ==============================
sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)
voyage_days = (sailing_time / 24) + port_stay
total_consumption = (sailing_time * consumption) + (port_stay * consumption)

# Biaya umum (sama untuk semua mode)
biaya_umum = {
    "Bunker BBM": total_consumption * harga_bunker,
    "Air Tawar": (voyage_days * 2) * harga_air_tawar,
    "Port Cost": port_cost * 2,
    "Premi": premi_nm * jarak,
    "Asist": asist_tug
}

# Biaya per Mode
if mode == "Owner":
    biaya_mode = {
        "Angsuran": (angsuran / 30) * voyage_days,
        "Crew Cost": (crew_cost / 30) * voyage_days,
        "Asuransi": (asuransi / 30) * voyage_days,
        "Docking": (docking / 30) * voyage_days,
        "Perawatan": (perawatan / 30) * voyage_days,
        "Sertifikat": (sertifikat / 30) * voyage_days,
        "Depresiasi": ((depresiasi / 15) / 12 / 30) * voyage_days,
        "Other": other_cost
    }
else:  # Charter
    biaya_mode = {
        "Charter Hire": (charter_hire / 30) * voyage_days,
        "Other": other_cost
    }

# Total Biaya
total_cost = sum(biaya_mode.values()) + sum(biaya_umum.values())
cost_per_mt = total_cost / total_cargo

# ==============================
# Ubah semua biaya ke format Rp
# ==============================
biaya_mode_rp = {k: f"Rp {v:,.0f}" for k, v in biaya_mode.items()}
biaya_umum_rp = {k: f"Rp {v:,.0f}" for k, v in biaya_umum.items()}

# ==============================
# Tampilkan Hasil Detail
# ==============================
st.header("📊 Hasil Perhitungan")

st.write(f"*Sailing Time (jam):* {sailing_time:,.2f}")
st.write(f"*Total Voyage Days:* {voyage_days:,.2f}")
st.write(f"*Total Consumption (liter):* {total_consumption:,.0f}")

st.subheader(f"💰 Biaya Mode ({mode})")
for k, v in biaya_mode_rp.items():
    st.write(f"- {k}: {v}")

st.subheader("💰 Biaya Umum")
for k, v in biaya_umum_rp.items():
    st.write(f"- {k}: {v}")

st.subheader("🧮 Total Cost")
st.write(f"*TOTAL COST: Rp {total_cost:,.0f}*")
st.subheader("🧮 Cost per MT")
st.write(f"*FREIGHT: Rp {cost_per_mt:,.0f} / MT*")

# ==============================
# Profit Scenario 0% - 50%
# ==============================
st.subheader("📈 Freight dengan Profit (0% - 50%)")
profit_list = []
for p in range(0, 55, 5):
    freight = cost_per_mt * (1 + (p / 100))
    revenue = freight * total_cargo
    net_profit = revenue - total_cost
    profit_list.append([f"{p}%", f"Rp {freight:,.0f}", f"Rp {revenue:,.0f}", f"Rp {net_profit:,.0f}"])
profit_df = pd.DataFrame(profit_list, columns=["Profit %", "Freight / MT", "Revenue", "Net Profit"])
st.table(profit_df)

# ==============================
# PDF Report
# ==============================
input_data = [
    ["POL", pol],
    ["POD", pod],
    ["Jarak (NM)", f"{jarak:,}"],
    ["Total Cargo (MT)", f"{total_cargo:,}"],
]
results = list(biaya_mode_rp.items()) + list(biaya_umum_rp.items())
results.append(["TOTAL COST", f"Rp {total_cost:,.0f}"])
results.append(["Cost per MT", f"Rp {cost_per_mt:,.0f} / MT"])

def generate_pdf(input_data, results, profit_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("🚢 Laporan Freight Tongkang", styles["Title"]))
    elements.append(Paragraph("📥 Input Utama", styles["Heading2"]))
    table_input = Table(input_data, colWidths=[200, 200])
    table_input.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

    ]))
    elements.append(table_input)
    elements.append(Spacer(0,0))

    elements.append(Paragraph("📊 Hasil Perhitungan", styles["Heading2"]))
    table_results = Table(results, colWidths=[200, 200])
    table_results.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(table_results)
    elements.append(Spacer(0,0))
    elements.append(Paragraph("📈 Skenario Profit (0% - 50%)", styles["Heading2"]))
    data_profit = [list(profit_df.columns)] + profit_df.values.tolist()
    table_profit = Table(data_profit, colWidths=[60,100,120,120])
    table_profit.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,0), colors.lightgrey),
        ("FONTNAME", (0,0), (0,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT")
    ]))
    elements.append(table_profit)

    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_buffer = generate_pdf(input_data, results, profit_df)

st.download_button(
    label="📥 Download Laporan PDF",
    data=pdf_buffer,
    file_name=f"Freight_Report_{pol}_{pod}.pdf",
    mime="application/pdf"
)

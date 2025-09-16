import streamlit as st
import pandas as pd

st.set_page_config(page_title="Freight Calculator", layout="wide")

st.title("🚢 Freight Calculator Batubara")

# ==============================
# Default Parameter (editable)
# ==============================
st.sidebar.header("⚙️ Parameter Default (Bisa diubah)")

speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=4.0)
consumption = st.sidebar.number_input("Consumption (liter/jam)", value=120)
harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=12500)

charter_hire = st.sidebar.number_input("Charter hire/bulan (Rp)", value=750000000)
crew_cost = st.sidebar.number_input("Crew cost/bulan (Rp)", value=60000000)
asuransi = st.sidebar.number_input("Asuransi/bulan (Rp)", value=50000000)
docking = st.sidebar.number_input("Docking Saving/bulan (Rp)", value=50000000)
perawatan = st.sidebar.number_input("Perawatan Fleet/bulan (Rp)", value=50000000)

port_cost = st.sidebar.number_input("Port cost/call (Rp)", value=50000000)
asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=35000000)
premi_nm = st.sidebar.number_input("Premi (Rp/NM)", value=50000)
Other_Cost = st.sidebar.number_input("Other Cost (Rp)", value=50000000)
port_stay = st.sidebar.number_input("Port Stay (Hari)", value=10)

# ==============================
# Input Utama dari User
# ==============================
st.header("📥 Input Utama")

pol = st.text_input("Port of Loading (POL)", value="Jetty SIP")
pod = st.text_input("Port of Discharge (POD)", value="Marunda")
jarak = st.number_input("Jarak (NM)", value=630)
total_cargo = st.number_input("Total Cargo (MT)", value=10000)

# ==============================
# Perhitungan
# ==============================
sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)
voyage_days = (sailing_time / 24) + port_stay
total_consumption = (sailing_time * consumption) + (port_stay * consumption)

biaya_charter = (charter_hire / 30) * voyage_days
biaya_bunker = total_consumption * harga_bunker
biaya_crew = (crew_cost / 30) * voyage_days
biaya_port = port_cost * 2
premi_cost = premi_nm * jarak
biaya_asist = asist_tug
other_cost = ((asuransi / 30) * voyage_days) + ((docking / 30) * voyage_days) + ((perawatan / 30) * voyage_days) + (Other_Cost)

total_cost = biaya_charter + biaya_bunker + biaya_crew + biaya_port + premi_cost + biaya_asist + other_cost
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


# --- Fungsi buat PDF ---
def generate_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Judul
    elements.append(Paragraph("Laporan Perhitungan Biaya Operasional Kapal", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Tanggal: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Voyage Info
    elements.append(Paragraph("1. Voyage Info", styles['Heading2']))
    data_voyage = [
        ["Port of Loading (POL)", pol],
        ["Port of Discharge (POD)", pod],
    ]
    table_voyage = Table(data_voyage, hAlign="LEFT")
    table_voyage.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    elements.append(table_voyage)
    elements.append(Spacer(1, 12))

    # Parameter Input
    elements.append(Paragraph("2. Parameter Input", styles['Heading2']))
    data_param = [
        ["Speed Kosong (knot)", speed_kosong],
        ["Speed Isi (knot)", speed_isi],
        ["Consumption (liter/jam)", consumption],
        ["Harga Bunker (Rp/liter)", f"Rp {harga_bunker:,.0f}"],
        ["Charter Hire (Rp/bulan)", f"Rp {charter_hire:,.0f}"],
        ["Crew Cost (Rp/bulan)", f"Rp {crew_cost:,.0f}"],
        ["Asuransi (Rp/bulan)", f"Rp {asuransi:,.0f}"],
    ]
    table_param = Table(data_param, hAlign="LEFT")
    table_param.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    elements.append(table_param)
    elements.append(Spacer(1, 12))

    # Hasil Perhitungan
    elements.append(Paragraph("3. Hasil Perhitungan", styles['Heading2']))
    data_hasil = [
        ["Biaya Bunker/bulan", f"Rp {biaya_bunker:,.0f}"],
        ["Charter Hire/bulan", f"Rp {charter_hire:,.0f}"],
        ["Crew Cost/bulan", f"Rp {crew_cost:,.0f}"],
        ["Asuransi/bulan", f"Rp {asuransi:,.0f}"],
        ["Total Biaya", f"Rp {total_biaya:,.0f}"]
    ]
    table_hasil = Table(data_hasil, hAlign="LEFT")
    table_hasil.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
    ]))
    elements.append(table_hasil)
    elements.append(Spacer(1, 20))

    # Catatan
    elements.append(Paragraph("4. Catatan:", styles['Heading2']))
    elements.append(Paragraph("Perhitungan ini bersifat estimasi dan dapat berubah sesuai kondisi operasional.", styles['Normal']))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# --- Tombol Download PDF ---
pdf_file = generate_pdf()
st.download_button(
    label="📥 Download Laporan PDF",
    data=pdf_file,
    file_name="laporan_biaya_operasional.pdf",
    mime="application/pdf"

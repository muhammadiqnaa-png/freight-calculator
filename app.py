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

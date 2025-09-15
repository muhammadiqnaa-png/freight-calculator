import streamlit as st
import pandas as pd

st.set_page_config(page_title="Freight Calculator", layout="wide")

st.title("⚓ Freight Calculator Batubara / Tongkang")
st.markdown("Masukkan **Jarak (NM)** dan **Cargo (MT)**, biaya akan dihitung otomatis dalam Rupiah.")

# ========================
# Parameter Default
# ========================
st.sidebar.header("⚙️ Parameter (bisa diedit)")

speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=4.0)
consumption_hour = st.sidebar.number_input("Consumption (liter/jam)", value=120)
consumption_day = consumption_hour * 24
harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=12500)

charter_day = st.sidebar.number_input("Charter hire/day (Rp)", value=750000000)
crew_day = st.sidebar.number_input("Crew cost/day (Rp)", value=60000000)
asuransi_day = st.sidebar.number_input("Asuransi/day (Rp)", value=50000000)
docking_day = st.sidebar.number_input("Docking Saving/day (Rp)", value=50000000)
perawatan_day = st.sidebar.number_input("Perawatan/day (Rp)", value=50000000)

port_cost = st.sidebar.number_input("Port cost/call (Rp)", value=50000000)
asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=35000000)
premi_nm = st.sidebar.number_input("Premi (Rp/NM)", value=50000)
port_stay = st.sidebar.number_input("Port Stay (Hari)", value=10)
cargo_capacity = st.sidebar.number_input("Cargo Capacity (MT)", value=10000)

# ========================
# Input Utama
# ========================
st.subheader("📥 Input Utama")
jarak = st.number_input("Jarak (NM)", value=630)
cargo = st.number_input("Total Cargo (MT)", value=10000)

# ========================
# Perhitungan
# ========================

# Sailing Time
sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)

# Voyage Days
voyage_days = sailing_time + port_stay

# Consumption
total_consumption = sailing_time * consumption_day

# Biaya-biaya
biaya_charter = charter_day * voyage_days
biaya_bunker = total_consumption * harga_bunker
biaya_crew = crew_day * voyage_days
biaya_port = port_cost * 2
biaya_premi = premi_nm * jarak
biaya_asist = asist_tug
biaya_other = (asuransi_day + docking_day + perawatan_day) * voyage_days

# Total Cost
total_cost = (
    biaya_charter + biaya_bunker + biaya_crew +
    biaya_port + biaya_premi + biaya_asist + biaya_other
)

# Cost per MT
cost_per_mt = total_cost / cargo_capacity

# ========================
# Output
# ========================

def format_rupiah(angka):
    return "Rp {:,.0f}".format(angka).replace(",", ".")

st.subheader("📊 Hasil Perhitungan")

col1, col2 = st.columns(2)

with col1:
    st.metric("⛴️ Sailing Time (hari)", f"{sailing_time:,.2f}")
    st.metric("📅 Total Voyage Days", f"{voyage_days:,.2f}")
    st.metric("⛽ Total Consumption (liter)", f"{total_consumption:,.0f}")

with col2:
    st.metric("💰 Total Cost", format_rupiah(total_cost))
    st.metric("📦 Cost per MT", format_rupiah(cost_per_mt))

# ========================
# Freight + Profit Table
# ========================
st.subheader("📈 Freight dengan Profit Margin")

profits = list(range(0, 55, 5))
data = {
    "Profit %": [f"{p}%" for p in profits],
    "Freight (Rp/MT)": [format_rupiah(cost_per_mt * (1 + p/100)) for p in profits]
}
df = pd.DataFrame(data)

st.dataframe(df, use_container_width=True)

st.success("✅ Masukkan **Jarak** dan **Cargo**, hasil otomatis muncul dalam Rupiah!")

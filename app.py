import streamlit as st
import pandas as pd

st.title("🚢 Freight Calculator Batubara")

st.sidebar.header("Input Parameters")

# Input utama
cargo = st.sidebar.number_input("Total Cargo (MT)", value=10000)
jarak = st.sidebar.number_input("Jarak (NM)", value=630)

# Parameter default (bisa di-edit user)
speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=4.0)
consumption_per_jam = st.sidebar.number_input("Consumption (liter/jam)", value=120)
harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=12500)

charter_hire_day = st.sidebar.number_input("Charter Hire per Hari (Rp)", value=25000000)
crew_day = st.sidebar.number_input("Crew Cost per Hari (Rp)", value=2000000)
asuransi_day = st.sidebar.number_input("Asuransi per Hari (Rp)", value=1666667)
docking_day = st.sidebar.number_input("Docking-Saving per Hari (Rp)", value=1666667)
perawatan_day = st.sidebar.number_input("Perawatan Fleet per Hari (Rp)", value=1666667)

port_cost = st.sidebar.number_input("Port Cost per Call (Rp)", value=50000000)
asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=35000000)
premi_nm = st.sidebar.number_input("Premi per NM (Rp)", value=50000)
port_stay = st.sidebar.number_input("Port Stay (Hari)", value=10)

# --- Perhitungan ---
consumption_per_hari = consumption_per_jam * 24

sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)
voyage_days = sailing_time + port_stay
total_consumption = sailing_time * consumption_per_hari

biaya_charter = charter_hire_day * voyage_days
biaya_bunker = total_consumption * harga_bunker
biaya_crew = crew_day * voyage_days
biaya_port = port_cost * 2
premi_cost = premi_nm * jarak
other_cost = (asuransi_day + docking_day + perawatan_day) * voyage_days

total_cost = biaya_charter + biaya_bunker + biaya_crew + biaya_port + premi_cost + asist_tug + other_cost
cost_per_mt = total_cost / cargo

# --- Buat tabel profit 0-50% ---
profit_list = []
for p in range(0, 55, 5):
    freight = cost_per_mt * (1 + p/100)
    profit_list.append({"Profit %": f"{p}%", "Freight (Rp/MT)": round(freight, 0)})

df = pd.DataFrame(profit_list)

st.subheader("📊 Freight Table dengan Profit")
st.dataframe(df, use_container_width=True)

# Tampilkan juga ringkasan biaya
st.subheader("📌 Ringkasan Biaya Utama")
st.write(f"Sailing Time: {sailing_time:.2f} hari")
st.write(f"Total Voyage Days: {voyage_days:.2f} hari")
st.write(f"Total Consumption: {total_consumption:,.0f} liter")
st.write(f"Total Cost: Rp {total_cost:,.0f}")
st.write(f"Cost per MT: Rp {cost_per_mt:,.0f}")

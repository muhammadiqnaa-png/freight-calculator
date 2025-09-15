import streamlit as st
import pandas as pd

st.set_page_config(page_title="Freight Calculator", layout="wide")

st.title("🚢 Freight Calculator - Batubara / Tongkang")

st.markdown("Masukkan parameter di bawah, lalu lihat hasil perhitungan Freight + Profit otomatis.")

# ===================== INPUT DEFAULT =====================
col1, col2 = st.columns(2)

with col1:
    speed_kosong = st.number_input("Speed Kosong (knots)", value=3.0)
    speed_isi = st.number_input("Speed Isi (knots)", value=4.0)
    consumption_per_hour = st.number_input("Consumption (liter/jam)", value=120.0)
    harga_bunker = st.number_input("Harga Bunker (Rp/liter)", value=12500)
    charter_hire_day = st.number_input("Charter Hire per Hari (Rp)", value=25000000)
    crew_cost_day = st.number_input("Crew Cost per Hari (Rp)", value=2000000)
    asuransi_day = st.number_input("Asuransi per Hari (Rp)", value=1666667)

with col2:
    docking_day = st.number_input("Docking Saving per Hari (Rp)", value=1666667)
    perawatan_day = st.number_input("Perawatan Fleet per Hari (Rp)", value=1666667)
    port_cost = st.number_input("Port Cost per Call (Rp)", value=50000000)
    asist_tug = st.number_input("Assist Tug (Rp)", value=35000000)
    premi_nm = st.number_input("Premi per NM (Rp)", value=50000)
    port_stay = st.number_input("Port Stay (Hari)", value=10)
    cargo_capacity = st.number_input("Cargo Capacity (MT)", value=10000)

# ===================== INPUT VARIABLE =====================
st.subheader("📥 Input Variabel")
col3, col4 = st.columns(2)
with col3:
    total_cargo = st.number_input("Total Cargo (MT)", value=10000)
with col4:
    jarak = st.number_input("Jarak (NM)", value=630)

# ===================== PERHITUNGAN =====================
# Sailing time (jam)
sailing_time_hours = (jarak / speed_kosong + jarak / speed_isi)
sailing_time_days = sailing_time_hours / 24

# Total voyage
total_voyage_days = sailing_time_days + port_stay

# Consumption
total_consumption = sailing_time_hours * consumption_per_hour

# Biaya
biaya_charter = charter_hire_day * total_voyage_days
biaya_bunker = total_consumption * harga_bunker
biaya_crew = crew_cost_day * total_voyage_days
biaya_port = port_cost * 2
biaya_premi = premi_nm * jarak
biaya_other = (asuransi_day + docking_day + perawatan_day) * total_voyage_days
biaya_asist_tug = asist_tug

total_biaya = biaya_charter + biaya_bunker + biaya_crew + biaya_port + biaya_premi + biaya_other + biaya_asist_tug

# Cost per MT
cost_per_mt = total_biaya / cargo_capacity

# ===================== OUTPUT =====================
st.subheader("📊 Hasil Perhitungan")
st.write(f"**Total Voyage Days:** {total_voyage_days:.2f} hari")
st.write(f"**Total Consumption:** {total_consumption:,.0f} liter")
st.write(f"**Total Biaya:** Rp {total_biaya:,.0f}")
st.write(f"**Cost per MT:** Rp {cost_per_mt:,.0f}")

# ===================== PROFIT SIMULATION =====================
st.subheader("💰 Simulasi Profit (0% - 50%)")

profit_list = []
for p in range(0, 55, 5):
    freight = cost_per_mt * (1 + p/100)
    profit_list.append([f"{p}%", f"Rp {freight:,.0f}"])

df_profit = pd.DataFrame(profit_list, columns=["Profit %", "Freight (Rp/MT)"])
st.dataframe(df_profit, use_container_width=True)

st.success("✅ Perhitungan selesai! Ubah input di atas untuk simulasi baru.")


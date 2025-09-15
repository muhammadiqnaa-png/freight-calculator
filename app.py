import streamlit as st
import pandas as pd

st.title("Freight Cost Calculator")

# ===== PARAMETER BISA DI EDIT =====
st.sidebar.header("Parameter (Bisa di-edit)")
speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=4.0)
consumption = st.sidebar.number_input("Consumption (liter/jam)", value=120)
harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=12500)
charter_hire = st.sidebar.number_input("Charter hire/bulan (Rp)", value=750_000_000)
crew_cost = st.sidebar.number_input("Crew cost/bulan (Rp)", value=60_000_000)
asuransi = st.sidebar.number_input("Asuransi/bulan (Rp)", value=50_000_000)
docking = st.sidebar.number_input("Docking-Saving/bulan (Rp)", value=50_000_000)
fleet = st.sidebar.number_input("Perawatan Fleet/bulan (Rp)", value=50_000_000)
port_cost = st.sidebar.number_input("Port cost/call (Rp)", value=50_000_000)
asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=35_000_000)
premi_nm = st.sidebar.number_input("Premi (NM)", value=50)
port_stay = st.sidebar.number_input("Port Stay (POL+POD, hari)", value=10)

# ===== INPUT UTAMA =====
st.header("Input Utama")
total_cargo = st.number_input("Total Cargo (MT)", value=10000)
jarak = st.number_input("Jarak (NM)", value=630)

# ===== HITUNG =====
sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)
total_voyage_days = (sailing_time / 24) + port_stay
total_consumption = (sailing_time * consumption) + (port_stay * consumption)
biaya_charter = (charter_hire / 30) * total_voyage_days
biaya_bunker = total_consumption * harga_bunker
biaya_crew = (crew_cost / 30) * total_voyage_days
biaya_port = port_cost * 2
premi_cost = premi_nm * jarak
other_cost = ((asuransi/30 + docking/30 + fleet/30) * total_voyage_days)
total_cost = biaya_charter + biaya_bunker + biaya_crew + biaya_port + premi_cost + asist_tug + other_cost
cost_per_mt = total_cost / total_cargo

# ===== HITUNG FREIGHT DENGAN PROFIT 0%-50% =====
profit_percent = list(range(0, 51, 5))  # 0%,5%,...,50%
freight_list = [cost_per_mt*(1+p/100) for p in profit_percent]
freight_df = pd.DataFrame({
    "Profit (%)": profit_percent,
    "Freight per MT (Rp)": [round(f,0) for f in freight_list]
})

# ===== TAMPILKAN =====
st.subheader("Hasil Perhitungan")
st.write(f"Sailing Time (jam): {round(sailing_time,2)}")
st.write(f"Total Voyage Days: {round(total_voyage_days,2)}")
st.write(f"Total Consumption (liter): {round(total_consumption,2)}")
st.write(f"Total Cost (Rp): {round(total_cost,0)}")
st.write(f"Cost per MT (Rp): {round(cost_per_mt,0)}")

st.subheader("Freight per MT dengan Profit 0%-50%")
st.dataframe(freight_df)

# ===== SIMPAN DATA =====
if st.button("Save Data"):
    freight_df.to_csv("freight_result.csv", index=False)
    st.success("Data tersimpan ke file 'freight_result.csv'")

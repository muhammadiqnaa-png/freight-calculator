import streamlit as st
import pandas as pd

# -------------------------------
# Judul Aplikasi
st.title("Perhitungan Freight Per MT")

# -------------------------------
# Parameter yang bisa diedit
st.header("Parameter (Bisa di Edit)")
speed_kosong = st.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.number_input("Speed Isi (knot)", value=4.0)
consumption = st.number_input("Consumption (liter/jam)", value=120)
harga_bunker = st.number_input("Harga Bunker (Rp/liter)", value=12500)
charter_hire = st.number_input("Charter hire/bulan (Rp)", value=750_000_000)
crew_cost = st.number_input("Crew cost/bulan (Rp)", value=60_000_000)
asuransi = st.number_input("Asuransi/Bulan (Rp)", value=50_000_000)
docking = st.number_input("Docking - Saving/Bulan (Rp)", value=50_000_000)
perawatan = st.number_input("Perawatan Fleet - Saving/Bulan (Rp)", value=50_000_000)
port_cost = st.number_input("Port cost/call (Rp)", value=50_000_000)
asist_tug = st.number_input("Asist Tug (Rp)", value=35_000_000)
premi_nm = st.number_input("Premi (Rp/NM)", value=50_000)
port_stay = st.number_input("Port Stay (POL&POD) (Hari)", value=10)

# -------------------------------
# Input utama dari user
st.header("Input Utama")
total_cargo = st.number_input("Total Cargo (MT)", value=10000)
jarak = st.number_input("Jarak (NM)", value=630)

# -------------------------------
# Hitung Sailing Time
sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)  # jam
total_voyage_days = (sailing_time / 24) + port_stay

# Total Consumption
total_consumption = (sailing_time * consumption) + (port_stay * consumption * 24 / 24)  # Ltr

# Biaya per komponen
biaya_charter = (charter_hire / 30) * total_voyage_days
biaya_bunker = total_consumption * harga_bunker
biaya_crew = (crew_cost / 30) * total_voyage_days
biaya_port = port_cost * 2
premi_cost = premi_nm * jarak
other_cost = ((asuransi / 30) * total_voyage_days) + \
             ((docking / 30) * total_voyage_days) + \
             ((perawatan / 30) * total_voyage_days)
total_cost = biaya_charter + biaya_bunker + biaya_crew + biaya_port + premi_cost + asist_tug + other_cost
cost_per_mt = total_cost / total_cargo

# -------------------------------
# Tampilkan hasil
st.header("Hasil Perhitungan")
st.write(f"*Sailing Time (Jam):* {sailing_time:.2f}")
st.write(f"*Total Voyage Days:* {total_voyage_days:.2f}")
st.write(f"*Total Consumption (Ltr):* {total_consumption:.2f}")
st.write(f"*Total Cost (Rp):* {total_cost:,.0f}")
st.write(f"*Cost per MT (Rp/MT):* {cost_per_mt:,.0f}")

# -------------------------------
# Freight per MT dengan Profit 0% - 50%
st.header("Freight per MT dengan Profit 0% - 50%")
profit_percent = [i for i in range(0, 51, 5)]
freight_list = [(p, cost_per_mt * (1 + p/100)) for p in profit_percent]
df_freight = pd.DataFrame(freight_list, columns=["Profit (%)", "Freight per MT (Rp)"])
st.dataframe(df_freight)

# -------------------------------
# Simpan / Load Data
st.header("Simpan / Load Data")
import json

def save_data(filename="voyage_data.json"):
    data = {
        "parameters": {
            "speed_kosong": speed_kosong,
            "speed_isi": speed_isi,
            "consumption": consumption,
            "harga_bunker": harga_bunker,
            "charter_hire": charter_hire,
            "crew_cost": crew_cost,
            "asuransi": asuransi,
            "docking": docking,
            "perawatan": perawatan,
            "port_cost": port_cost,
            "asist_tug": asist_tug,
            "premi_nm": premi_nm,
            "port_stay": port_stay
        },
        "input_user": {
            "total_cargo": total_cargo,
            "jarak": jarak
        },
        "results": {
            "sailing_time": sailing_time,
            "total_voyage_days": total_voyage_days,
            "total_consumption": total_consumption,
            "total_cost": total_cost,
            "cost_per_mt": cost_per_mt,
            "freight_list": freight_list
        }
    }
    with open(filename, "w") as f:
        json.dump(data, f)
    st.success(f"Data berhasil disimpan di {filename}")

def load_data(filename="voyage_data.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        st.success(f"Data berhasil di-load dari {filename}")
        st.json(data)
    except:
        st.error("Gagal load data!")

if st.button("Save Data"):
    save_data()

if st.button("Load Data"):
    load_data()

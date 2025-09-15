import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kalkulator Freight Rupiah 🚢", layout="wide")

st.title("🚢 Kalkulator Freight (Rupiah)")
st.write("Hitung biaya operasional & profit otomatis, mirip format Excel.")

# --- Input (seperti kolom kuning di Excel) ---
st.sidebar.header("Input Data")

jarak = st.sidebar.number_input("Jarak (Mil Laut)", min_value=0.0, step=10.0)
tarif_per_mil = st.sidebar.number_input("Tarif per Mil (Rp)", min_value=0.0, step=1000.0)
biaya_lain = st.sidebar.number_input("Biaya Lain (Rp)", min_value=0.0, step=10000.0)

# --- Hitungan ---
operasional_cost = jarak * tarif_per_mil + biaya_lain

# Profit margin list (0% - 50%)
margin_list = list(range(0, 55, 5))
data = []
for m in margin_list:
    harga_jual = operasional_cost * (1 + m/100)
    profit = harga_jual - operasional_cost
    data.append([f"{m}%", f"Rp {operasional_cost:,.0f}", f"Rp {profit:,.0f}", f"Rp {harga_jual:,.0f}"])

# --- Tabel Hasil ---
df = pd.DataFrame(data, columns=["Margin", "Operasional Cost", "Profit", "Harga Jual"])

st.subheader("📊 Hasil Perhitungan")
st.dataframe(df, use_container_width=True)

# --- Download ke Excel ---
st.download_button(
    "📥 Download Hasil (Excel)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="freight_calculation_rupiah.csv",
    mime="text/csv"
)

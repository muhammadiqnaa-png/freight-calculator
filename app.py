import streamlit as st
import pandas as pd

st.set_page_config(page_title="Freight Calculator 🚢", layout="wide")

st.title("🚢 Freight Calculator")
st.write("Hitung estimasi biaya cargo dengan mudah.")

# --- Input data dari user ---
st.sidebar.header("Input Data")

cargo_name = st.sidebar.text_input("Nama Cargo", "Coal")
quantity = st.sidebar.number_input("Jumlah Muatan (MT)", min_value=0.0, step=100.0)
freight_rate = st.sidebar.number_input("Freight Rate (USD/MT)", min_value=0.0, step=0.5)
other_cost = st.sidebar.number_input("Biaya Lain (USD)", min_value=0.0, step=10.0)

# --- Perhitungan ---
total_freight = quantity * freight_rate
grand_total = total_freight + other_cost

# --- Output ---
st.subheader("📊 Hasil Perhitungan")
st.write(f"**Cargo**: {cargo_name}")
st.write(f"**Jumlah Muatan**: {quantity:,.2f} MT")
st.write(f"**Freight Rate**: {freight_rate:,.2f} USD/MT")
st.write(f"**Total Freight**: {total_freight:,.2f} USD")
st.write(f"**Biaya Lain**: {other_cost:,.2f} USD")
st.success(f"💰 **Grand Total: {grand_total:,.2f} USD**")

# --- Export ke Excel ---
df = pd.DataFrame({
    "Cargo": [cargo_name],
    "Quantity (MT)": [quantity],
    "Freight Rate (USD/MT)": [freight_rate],
    "Total Freight (USD)": [total_freight],
    "Other Cost (USD)": [other_cost],
    "Grand Total (USD)": [grand_total]
})

st.download_button(
    "📥 Download Hasil (Excel)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="freight_calculation.csv",
    mime="text/csv"
)

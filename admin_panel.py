import streamlit as st
import pandas as pd
import requests
from io import BytesIO


def show_admin_panel():

    st.sidebar.markdown("### 👑 Admin Panel")

    with st.sidebar.expander("📊 History Calculate Report", expanded=False):

        url = "https://freight-calculator-2b823-default-rtdb.asia-southeast1.firebasedatabase.app/calculate_history.json"

        try:
            res = requests.get(url)
            data = res.json()

            if not data:
                st.info("Belum ada data")
            else:
                records = []

                for item in data.values():

                    cargo = item.get("cargo") or item.get("cargo_type") or item.get("type_cargo")
                    qty = item.get("qty")
                    email = item.get("email")

                    if isinstance(qty, str) and "MT" in qty:
                        cargo = qty
                        qty = None

                    if isinstance(email, (int, float)):
                        email = "-"

                    records.append({
                        "Date": item.get("date"),
                        "POL": item.get("pol"),
                        "POD": item.get("pod"),
                        "Cargo": item.get("type_cargo"),
                        "Qty": item.get("qty"),
                        "Freight Input": item.get("freight_input"),
                        "Freight Cost": item.get("freight_cost"),
                        "Fuel Price": item.get("fuel_price"),
                        "User": item.get("email"),
                    })

                df = pd.DataFrame(records)

                # ===== EXCEL EXPORT FUNCTION =====
                def to_excel(df):
                    output = BytesIO()

                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="History Calculate")

                        worksheet = writer.sheets["History Calculate"]

                        for i, col in enumerate(df.columns):
                            try:
                                max_len = max(
                                    df[col].astype(str).fillna("").map(len).max(),
                                    len(str(col))
                                )
                                worksheet.column_dimensions[chr(65 + i)].width = max_len + 3
                            except:
                                worksheet.column_dimensions[chr(65 + i)].width = 15

                    return output.getvalue()

                # sort terbaru
                if "Date" in df.columns:
                    df = df.sort_values(by="Date", ascending=False)

                # format angka
                for col in ["Freight Input", "Freight Cost", "Fuel Price"]:
                    if col in df.columns:
                        df[col] = df[col].apply(
                            lambda x: f"Rp {x:,.0f}" if pd.notnull(x) else "-"
                        )

                st.dataframe(df, use_container_width=True, height=300)

                excel_data = to_excel(df)

                st.download_button(
                    label="📥 Download Excel Report",
                    data=excel_data,
                    file_name="History_Calculate.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Error load admin data: {e}")

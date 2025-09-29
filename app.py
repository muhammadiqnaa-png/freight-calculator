import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

DB_PATH = "data.db"

# ==============================
# Database Setup
# ==============================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Drop table lama kalau strukturnya beda
    try:
        c.execute("PRAGMA table_info(kapal)")
        cols = [row[1] for row in c.fetchall()]
        required = ["id","nama","total_cargo","consumption","angsuran","crew_cost","asuransi","docking","perawatan","sertifikat","depresiasi","charter_hire"]
        if set(required) - set(cols):
            c.execute("DROP TABLE IF EXISTS kapal")
    except:
        pass
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS kapal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT UNIQUE,
            total_cargo REAL,
            consumption REAL,
            angsuran REAL,
            crew_cost REAL,
            asuransi REAL,
            docking REAL,
            perawatan REAL,
            sertifikat REAL,
            depresiasi REAL,
            charter_hire REAL
        )
    """)
    conn.commit()
    conn.close()


def tambah_kapal(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO kapal (nama,total_cargo,consumption,angsuran,crew_cost,asuransi,docking,perawatan,sertifikat,depresiasi,charter_hire)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, data)
    conn.commit()
    conn.close()

def get_all_kapal():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM kapal", conn)
    conn.close()
    return df

def get_kapal_by_name(nama):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM kapal WHERE nama=?", (nama,))
    row = c.fetchone()
    conn.close()
    return row

# ==============================
# Init
# ==============================
st.set_page_config(page_title="Freight Calculator", layout="wide")
init_db()

# ==============================
# Login sederhana
# ==============================
USER_CREDENTIALS = {"admin": "12345", "user1": "abcde"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔒 Login Aplikasi Freight Calculator")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Username / password salah")
else:
    st.sidebar.success("Login sebagai: " + st.session_state.username)
    st.title("🚢 Freight Calculator Tongkang")

    # ==============================
    # Pilih Kapal
    # ==============================
    df_kapal = get_all_kapal()
    kapal_list = ["-- Kapal Baru --"] + df_kapal["nama"].tolist()
    pilihan_kapal = st.sidebar.selectbox("Pilih Kapal", kapal_list)

    kapal_data = None
    if pilihan_kapal != "-- Kapal Baru --":
        row = get_kapal_by_name(pilihan_kapal)
        if row:
            _, nama, total_cargo_db, consumption_db, angsuran_db, crew_cost_db, asuransi_db, docking_db, perawatan_db, sertifikat_db, depresiasi_db, charter_hire_db = row
            kapal_data = dict(
                nama=nama,
                total_cargo=total_cargo_db,
                consumption=consumption_db,
                angsuran=angsuran_db,
                crew_cost=crew_cost_db,
                asuransi=asuransi_db,
                docking=docking_db,
                perawatan=perawatan_db,
                sertifikat=sertifikat_db,
                depresiasi=depresiasi_db,
                charter_hire=charter_hire_db
            )

    # ==============================
    # Input Utama
    # ==============================
    st.header("📥 Input Utama")
    pol = st.text_input("Port of Loading (POL)")
    pod = st.text_input("Port of Discharge (POD)")

    total_cargo = st.number_input("Total Cargo (MT)", value=kapal_data["total_cargo"] if kapal_data else 7500)
    jarak = st.number_input("Jarak (NM)", value=630)

    # ==============================
    # Sidebar Parameter
    # ==============================
    st.sidebar.header("⚙️ Parameter")

    speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=3.0)
    speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=4.0)
    consumption = st.sidebar.number_input("Consumption (liter/jam)", value=kapal_data["consumption"] if kapal_data else 120)
    harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=12500)
    harga_air_tawar = st.sidebar.number_input("Harga Air Tawar (Rp/Ton)", value=120000)
    port_cost = st.sidebar.number_input("Port cost/call (Rp)", value=50000000)
    asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=35000000)
    premi_nm = st.sidebar.number_input("Premi (Rp/NM)", value=50000)

    mode = st.radio("Pilih Mode Biaya:", ["Owner", "Charter"])

    if mode == "Owner":
        angsuran = st.sidebar.number_input("Angsuran (Rp/bulan)", value=kapal_data["angsuran"] if kapal_data else 750000000)
        crew_cost = st.sidebar.number_input("Crew Cost (Rp/bulan)", value=kapal_data["crew_cost"] if kapal_data else 60000000)
        asuransi = st.sidebar.number_input("Asuransi (Rp/bulan)", value=kapal_data["asuransi"] if kapal_data else 50000000)
        docking = st.sidebar.number_input("Docking (Rp/bulan)", value=kapal_data["docking"] if kapal_data else 50000000)
        perawatan = st.sidebar.number_input("Perawatan (Rp/bulan)", value=kapal_data["perawatan"] if kapal_data else 50000000)
        sertifikat = st.sidebar.number_input("Sertifikat (Rp/bulan)", value=kapal_data["sertifikat"] if kapal_data else 50000000)
        depresiasi = st.sidebar.number_input("Depresiasi (Rp/Beli)", value=kapal_data["depresiasi"] if kapal_data else 45000000000)
        other_cost = st.sidebar.number_input("Other Cost (Rp)", value=50000000)
    else:
        charter_hire = st.sidebar.number_input("Charter Hire (Rp/bulan)", value=kapal_data["charter_hire"] if kapal_data else 750000000)
        other_cost = st.sidebar.number_input("Other Cost (Rp)", value=50000000)

    port_stay = st.sidebar.number_input("Port Stay (Hari)", value=10)

    # ==============================
    # Simpan Kapal
    # ==============================
    with st.sidebar.expander("💾 Simpan/Update Kapal"):
        nama_kapal_input = st.text_input("Nama Kapal", value=kapal_data["nama"] if kapal_data else "")
        if st.button("Simpan Kapal"):
            data = (
                nama_kapal_input,
                total_cargo,
                consumption,
                angsuran if mode=="Owner" else None,
                crew_cost if mode=="Owner" else None,
                asuransi if mode=="Owner" else None,
                docking if mode=="Owner" else None,
                perawatan if mode=="Owner" else None,
                sertifikat if mode=="Owner" else None,
                depresiasi if mode=="Owner" else None,
                charter_hire if mode=="Charter" else None
            )
            tambah_kapal(data)
            st.success("Data kapal berhasil disimpan/diupdate!")
            st.rerun()

    # ==============================
    # Perhitungan
    # ==============================
    sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)
    voyage_days = (sailing_time / 24) + port_stay
    total_consumption = (sailing_time * consumption) + (port_stay * consumption)

    biaya_umum = {
        "Bunker BBM": total_consumption * harga_bunker,
        "Air Tawar": (voyage_days * 2) * harga_air_tawar,
        "Port Cost": port_cost * 2,
        "Premi": premi_nm * jarak,
        "Asist": asist_tug
    }

    if mode == "Owner":
        biaya_mode = {
            "Angsuran": (angsuran / 30) * voyage_days,
            "Crew Cost": (crew_cost / 30) * voyage_days,
            "Asuransi": (asuransi / 30) * voyage_days,
            "Docking": (docking / 30) * voyage_days,
            "Perawatan": (perawatan / 30) * voyage_days,
            "Sertifikat": (sertifikat / 30) * voyage_days,
            "Depresiasi": ((depresiasi / 15) / 12 / 30) * voyage_days,
            "Other": other_cost
        }
    else:
        biaya_mode = {
            "Charter Hire": (charter_hire / 30) * voyage_days,
            "Other": other_cost
        }

    total_cost = sum(biaya_umum.values()) + sum(biaya_mode.values())
    cost_per_mt = total_cost / total_cargo

    # ==============================
    # Output
    # ==============================
    st.header("📊 Hasil Perhitungan")
    st.write(f"Sailing Time (jam): {sailing_time:,.2f}")
    st.write(f"Total Voyage Days: {voyage_days:,.2f}")
    st.write(f"Total Consumption (liter): {total_consumption:,.0f}")

    st.subheader(f"💰 Biaya Mode ({mode})")
    for k,v in biaya_mode.items():
        st.write(f"- {k}: Rp {v:,.0f}")

    st.subheader("💰 Biaya Umum")
    for k,v in biaya_umum.items():
        st.write(f"- {k}: Rp {v:,.0f}")

    st.subheader("🧮 Total Cost")
    st.write(f"TOTAL COST: Rp {total_cost:,.0f}")
    st.subheader("🧮 Cost per MT")
    st.write(f"FREIGHT: Rp {cost_per_mt:,.0f} / MT")

    st.subheader("📈 Freight dengan Profit (0% - 50%)")
    profit_list = []
    for p in range(0,55,5):
        freight = cost_per_mt * (1+p/100)
        revenue = freight * total_cargo
        Pph = revenue * 0.012
        net_profit = revenue - Pph - total_cost
        profit_list.append([f"{p}%", f"Rp {freight:,.0f}", f"Rp {revenue:,.0f}", f"Rp {Pph:,.0f}", f"Rp {net_profit:,.0f}"])
    profit_df = pd.DataFrame(profit_list, columns=["Profit %","Freight / MT","Revenue","Pph","Net Profit"])
    st.table(profit_df)

    # ==============================
    # PDF Export
    # ==============================
    input_data = [["POL", pol],["POD", pod],["Jarak (NM)", f"{jarak:,}"],["Total Cargo (MT)", f"{total_cargo:,}"],["Voyage Days", f"{voyage_days:,.2f} hari"]]
    results = list(biaya_mode.items()) + list(biaya_umum.items())
    results.append(["TOTAL COST", total_cost])
    results.append(["Cost per MT", cost_per_mt])

    def generate_pdf(input_data, results, profit_df):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("🚢 Laporan Freight Tongkang", styles["Title"]))
        elements.append(Spacer(1,12))

        elements.append(Paragraph("📥 Input Utama", styles["Heading2"]))
        table_input = Table(input_data, colWidths=[200,200])
        table_input.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(table_input)
        elements.append(Spacer(1,12))

        elements.append(Paragraph("📊 Hasil Perhitungan", styles["Heading2"]))
        table_results = Table([[k,f"Rp {v:,.0f}" if isinstance(v,(int,float)) else v] for k,v in results], colWidths=[200,200])
        table_results.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(table_results)
        elements.append(Spacer(1,12))

        elements.append(Paragraph("📈 Skenario Profit (0% - 50%)", styles["Heading2"]))
        data_profit = [list(profit_df.columns)] + profit_df.values.tolist()
        table_profit = Table(data_profit, colWidths=[60,100,120,120,120])
        table_profit.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(table_profit)
        doc.build(elements)
        buffer.seek(0)
        return buffer

    pdf_buffer = generate_pdf(input_data, results, profit_df)
    st.download_button("📥 Download Laporan PDF", data=pdf_buffer, file_name=f"Freight_Report_{pol or 'POL'}_{pod or 'POD'}.pdf", mime="application/pdf")

    # Logout
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

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
# Database Setup (safe, auto-alter)
# ==============================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    required_cols = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "nama": "TEXT UNIQUE",
        "total_cargo": "REAL",
        "consumption": "REAL",
        "angsuran": "REAL",
        "crew_cost": "REAL",
        "asuransi": "REAL",
        "docking": "REAL",
        "perawatan": "REAL",
        "sertifikat": "REAL",
        "depresiasi": "REAL",
        "charter_hire": "REAL"
    }

    # create table if not exists (with all required cols as a baseline)
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS kapal (
            {", ".join([f"{col} {dtype}" for col, dtype in required_cols.items()])}
        )
    """)

    # get existing cols and add missing ones (ALTER TABLE)
    c.execute("PRAGMA table_info(kapal)")
    existing_cols = [row[1] for row in c.fetchall()]
    for col, dtype in required_cols.items():
        if col not in existing_cols:
            # NOTE: SQLite will ignore PRIMARY KEY re-declaration if column exists;
            # but since col not in existing_cols, safe to add simple column (skip PK if needed)
            try:
                # avoid adding PK via ALTER (it will fail), so add without PK if col == id and table exists
                if col == "id":
                    # skip adding id if table already existed without it (rare)
                    continue
                c.execute(f"ALTER TABLE kapal ADD COLUMN {col} {dtype}")
            except Exception:
                pass

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

def hapus_kapal(nama):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM kapal WHERE nama=?", (nama,))
    conn.commit()
    conn.close()

def get_all_kapal():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM kapal", conn)
    except Exception:
        df = pd.DataFrame(columns=["id","nama","total_cargo","consumption","angsuran","crew_cost","asuransi","docking","perawatan","sertifikat","depresiasi","charter_hire"])
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
# Init app
# ==============================
st.set_page_config(page_title="Freight Calculator", layout="wide")
init_db()

# ==============================
# Simple auth (keep as you had)
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
    st.stop()

# ==============================
# Main UI (logged in)
# ==============================
st.sidebar.success("Login sebagai: " + st.session_state.username)
st.title("🚢 Freight Calculator Tongkang")

# ------------------------------
# SIDEBAR: Mode (top), Pilih Kapal, Params
# ------------------------------
st.sidebar.title("⚙️ Pengaturan Perhitungan")

# 1) Mode always at the very top
mode = st.sidebar.radio("Pilih Mode Biaya:", ["Owner", "Charter"])

# 2) Pilih kapal (below mode)
df_kapal = get_all_kapal()
kapal_names = df_kapal["nama"].dropna().tolist() if not df_kapal.empty else []
kapal_list = ["-- Kapal Baru --"] + kapal_names
pilihan_kapal = st.sidebar.selectbox("Pilih Kapal", kapal_list)

# load kapal data if selected
kapal_data = None
if pilihan_kapal != "-- Kapal Baru --":
    row = get_kapal_by_name(pilihan_kapal)
    if row:
        # unpack row safely (may have None columns)
        # row format: (id, nama, total_cargo, consumption, angsuran, crew_cost, asuransi, docking, perawatan, sertifikat, depresiasi, charter_hire)
        _, nama, total_cargo_db, consumption_db, angsuran_db, crew_cost_db, asuransi_db, docking_db, perawatan_db, sertifikat_db, depresiasi_db, charter_hire_db = row + (None,) * (12 - len(row))
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

# 3) Data Kapal (tersimpan)
st.sidebar.markdown("### 📦 Data Kapal (Tersimpan)")
# show read-only summary
if kapal_data:
    st.sidebar.write(f"**Kapal:** {kapal_data.get('nama')}")
    st.sidebar.write(f"**Total Cargo (MT):** {kapal_data.get('total_cargo'):,}" if kapal_data.get('total_cargo') else "Total Cargo (MT): -")
else:
    st.sidebar.info("Pilih kapal atau buat kapal baru")

# editable fields in Data Kapal section (values default from kapal_data if available)
consumption = st.sidebar.number_input(
    "Consumption (liter/jam)", 
    value=float(kapal_data["consumption"]) if kapal_data and kapal_data.get("consumption") is not None else 120
)

if mode == "Owner":
    angsuran = st.sidebar.number_input("Angsuran (Rp/bulan)", value=float(kapal_data["angsuran"]) if kapal_data and kapal_data.get("angsuran") is not None else 750000000)
    crew_cost = st.sidebar.number_input("Crew Cost (Rp/bulan)", value=float(kapal_data["crew_cost"]) if kapal_data and kapal_data.get("crew_cost") is not None else 60000000)
    asuransi = st.sidebar.number_input("Asuransi (Rp/bulan)", value=float(kapal_data["asuransi"]) if kapal_data and kapal_data.get("asuransi") is not None else 50000000)
    docking = st.sidebar.number_input("Docking (Rp/bulan)", value=float(kapal_data["docking"]) if kapal_data and kapal_data.get("docking") is not None else 50000000)
    perawatan = st.sidebar.number_input("Perawatan (Rp/bulan)", value=float(kapal_data["perawatan"]) if kapal_data and kapal_data.get("perawatan") is not None else 50000000)
    sertifikat = st.sidebar.number_input("Sertifikat (Rp/bulan)", value=float(kapal_data["sertifikat"]) if kapal_data and kapal_data.get("sertifikat") is not None else 50000000)
    depresiasi = st.sidebar.number_input("Depresiasi (Rp/Beli)", value=float(kapal_data["depresiasi"]) if kapal_data and kapal_data.get("depresiasi") is not None else 45000000000)
else:
    charter_hire = st.sidebar.number_input("Charter Hire (Rp/bulan)", value=float(kapal_data["charter_hire"]) if kapal_data and kapal_data.get("charter_hire") is not None else 750000000)

# 4) Parameter Voyage (sementara)
st.sidebar.markdown("### ⚓ Parameter Voyage (Sementara)")
speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=3.0)
speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=4.0)
harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=12500)
harga_air_tawar = st.sidebar.number_input("Harga Air Tawar (Rp/Ton)", value=120000)
port_cost = st.sidebar.number_input("Port cost/call (Rp)", value=50000000)
asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=35000000)
premi_nm = st.sidebar.number_input("Premi (Rp/NM)", value=50000)
other_cost = st.sidebar.number_input("Other Cost (Rp)", value=50000000)
port_stay = st.sidebar.number_input("Port Stay (Hari)", value=10)

# ------------------------------
# Simpan / Update / Hapus Kapal (expander)
# ------------------------------
with st.sidebar.expander("💾 Kelola Data Kapal"):
    nama_kapal_input = st.text_input("Nama Kapal", value=kapal_data["nama"] if kapal_data else "")
    total_cargo_input = st.number_input("Total Cargo (MT)", value=float(kapal_data["total_cargo"]) if kapal_data and kapal_data.get("total_cargo") is not None else 7500)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Simpan / Update"):
            if not nama_kapal_input.strip():
                st.sidebar.error("Nama kapal tidak boleh kosong.")
            else:
                data = (
                    nama_kapal_input.strip(),
                    total_cargo_input,
                    consumption,
                    angsuran if mode == "Owner" else None,
                    crew_cost if mode == "Owner" else None,
                    asuransi if mode == "Owner" else None,
                    docking if mode == "Owner" else None,
                    perawatan if mode == "Owner" else None,
                    sertifikat if mode == "Owner" else None,
                    depresiasi if mode == "Owner" else None,
                    charter_hire if mode == "Charter" else None
                )
                tambah_kapal(data)
                st.sidebar.success("✅ Data kapal berhasil disimpan / diupdate!")
                st.rerun()
    with col2:
        if pilihan_kapal != "-- Kapal Baru --" and st.button("❌ Hapus"):
            if nama_kapal_input.strip():
                hapus_kapal(nama_kapal_input.strip())
                st.sidebar.warning(f"Data kapal '{nama_kapal_input.strip()}' sudah dihapus.")
                st.rerun()
            else:
                st.sidebar.error("Nama kapal tidak ditemukan untuk dihapus.")
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()

# ==============================
# Main content: Input Voyage & Results
# ==============================
st.header("📥 Input Utama Voyage")
pol = st.text_input("Port of Loading (POL)")
pod = st.text_input("Port of Discharge (POD)")

total_cargo = st.number_input("Total Cargo (MT)", value=float(kapal_data["total_cargo"]) if kapal_data and kapal_data.get("total_cargo") is not None else 7500)
jarak = st.number_input("Jarak (NM)", value=630)

# Perhitungan
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
cost_per_mt = total_cost / total_cargo if total_cargo else 0

# Output
st.header("📊 Hasil Perhitungan")
st.write(f"Sailing Time (jam): {sailing_time:,.2f}")
st.write(f"Total Voyage Days: {voyage_days:,.2f}")
st.write(f"Total Consumption (liter): {total_consumption:,.0f}")

st.subheader(f"💰 Biaya Mode ({mode})")
for k, v in biaya_mode.items():
    st.write(f"- {k}: Rp {v:,.0f}")

st.subheader("💰 Biaya Umum")
for k, v in biaya_umum.items():
    st.write(f"- {k}: Rp {v:,.0f}")

st.subheader("🧮 Total Cost")
st.write(f"TOTAL COST: Rp {total_cost:,.0f}")
st.subheader("🧮 Cost per MT")
st.write(f"FREIGHT: Rp {cost_per_mt:,.0f} / MT")

st.subheader("📈 Freight dengan Profit (0% - 50%)")
profit_list = []
for p in range(0,55,5):
    freight = cost_per_mt * (1 + p/100)
    revenue = freight * total_cargo
    Pph = revenue * 0.012
    net_profit = revenue - Pph - total_cost
    profit_list.append([f"{p}%", f"Rp {freight:,.0f}", f"Rp {revenue:,.0f}", f"Rp {Pph:,.0f}", f"Rp {net_profit:,.0f}"])
profit_df = pd.DataFrame(profit_list, columns=["Profit %","Freight / MT","Revenue","Pph","Net Profit"])
st.table(profit_df)

# ==============================
# PDF Export (same as before)
# ==============================
input_data = [["POL", pol],["POD", pod],["Jarak (NM)", f"{jarak:,}"],["Total Cargo (MT)", f"{total_cargo:,}"],["Voyage Days", f"{voyage_days:,.2f} hari"]]
results = list(biaya_mode.items()) + list(biaya_umum.items())
results.append(["TOTAL COST", total_cost])
results.append(["Cost per MT", cost_per_mt])

def generate_pdf(input_data, results, profit_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20, leftMargin=20,
                            topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    style_title = styles["Title"]; style_title.fontSize = 14
    style_heading = styles["Heading2"]; style_heading.fontSize = 11
    style_normal = styles["Normal"]; style_normal.fontSize = 9

    elements.append(Paragraph("LAPORAN PERHITUNGAN FREIGHT", style_title))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("Input Utama", style_heading))
    table_input = Table(input_data, colWidths=[150, 300])
    table_input.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,-1), "LEFT")
    ]))
    elements.append(table_input)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Hasil Perhitungan", style_heading))
    table_results = Table(
        [[k, f"Rp {v:,.0f}" if isinstance(v, (int, float)) else v] for k, v in results],
        colWidths=[200, 250]
    )
    table_results.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,-1), "LEFT")
    ]))
    elements.append(table_results)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Skenario Profit (0% - 50%)", style_heading))
    data_profit = [list(profit_df.columns)] + profit_df.values.tolist()
    table_profit = Table(data_profit, colWidths=[60, 90, 100, 100, 100])
    table_profit.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (0,0), (-1,-1), "CENTER")
    ]))
    elements.append(table_profit)

    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_buffer = generate_pdf(input_data, results, profit_df)
st.download_button("📥 Download Laporan PDF", data=pdf_buffer,
                   file_name=f"Freight_Report_{pol or 'POL'}_{pod or 'POD'}.pdf",
                   mime="application/pdf")

# Logout
st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()

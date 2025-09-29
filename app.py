import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# Page config (call early)
# -----------------------------
st.set_page_config(page_title="Freight Calculator", layout="wide")

# ==============================
# Database (SQLite) helpers
# ==============================
DB_PATH = "data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS kapal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kapal TEXT UNIQUE,
            speed_kosong REAL,
            speed_isi REAL,
            consumption REAL,
            harga_bunker REAL,
            harga_air_tawar REAL,
            port_cost REAL,
            asist_tug REAL,
            premi_nm REAL,
            angsuran REAL,
            crew_cost REAL,
            asuransi REAL,
            docking REAL,
            perawatan REAL,
            sertifikat REAL,
            depresiasi REAL,
            other_cost REAL,
            charter_hire REAL,
            port_stay REAL
        )
    """)
    conn.commit()
    return conn

def tambah_kapal(data: dict):
    conn = init_db()
    c = conn.cursor()
    cols = ",".join(data.keys())
    placeholders = ",".join(["?"] * len(data))
    try:
        c.execute(f"INSERT INTO kapal ({cols}) VALUES ({placeholders})", tuple(data.values()))
        conn.commit()
        return True, "Berhasil menyimpan kapal."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def ambil_kapal_df():
    conn = init_db()
    try:
        df = pd.read_sql_query("SELECT * FROM kapal", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def get_kapal_by_name(nama):
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT * FROM kapal WHERE nama_kapal=?", (nama,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    cols = [d[0] for d in sqlite3.connect(DB_PATH).cursor().execute("PRAGMA table_info(kapal)").fetchall()]
    # fallback: build dict by index (safer)
    keys = ['id','nama_kapal','speed_kosong','speed_isi','consumption','harga_bunker','harga_air_tawar','port_cost','asist_tug','premi_nm','angsuran','crew_cost','asuransi','docking','perawatan','sertifikat','depresiasi','other_cost','charter_hire','port_stay']
    return dict(zip(keys, row))

def update_kapal_by_id(id_kapal, data: dict):
    conn = init_db()
    c = conn.cursor()
    assignments = ",".join([f"{k}=?" for k in data.keys()])
    try:
        c.execute(f"UPDATE kapal SET {assignments} WHERE id=?", tuple(data.values()) + (id_kapal,))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def hapus_kapal_by_id(id_kapal):
    conn = init_db()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM kapal WHERE id=?", (id_kapal,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

# ==============================
# User & Password (existing)
# ==============================
USER_CREDENTIALS = {
    "admin": "12345",
    "user1": "abcde"
}

# ==============================
# Session State Login
# ==============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ==============================
# Login Page
# ==============================
if not st.session_state.logged_in:
    st.title("🔒 Login Aplikasi Freight Calculator")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")
    if login_btn:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Login berhasil ✅ Selamat datang, {username}!")
            st.experimental_rerun()
        else:
            st.error("Username / password salah")

# ==============================
# Halaman Utama (hanya muncul setelah login)
# ==============================
else:
    st.sidebar.success("Login sebagai: " + st.session_state.username)
    st.title("🚢 Freight Calculator Tongkang")

    # ------------------
    # Sidebar: kapal selector & parameter
    # ------------------
    st.sidebar.header("⚓ Kapal (Database)")
    df_kapal = ambil_kapal_df()
    kapal_list = df_kapal['nama_kapal'].tolist() if not df_kapal.empty else []
    kapal_choice = st.sidebar.selectbox("Pilih Kapal (atau pilih 'Manual')", ["Manual"] + kapal_list)

    # helper to safely get float
    def safe(val, default=0.0):
        try:
            return float(val) if val is not None else default
        except:
            return default

    # if kapal selected, fetch its params
    kapal_params = None
    if kapal_choice != "Manual":
        kapal_row = get_kapal_by_name(kapal_choice)
        if kapal_row:
            kapal_params = kapal_row

    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Parameter (bisa otomatis dari Kapal)")

    # Default values (from DB if kapal selected, else fallbacks)
    speed_kosong = st.sidebar.number_input("Speed Kosong (knot)", value=safe(kapal_params.get('speed_kosong') if kapal_params else 3.0))
    speed_isi = st.sidebar.number_input("Speed Isi (knot)", value=safe(kapal_params.get('speed_isi') if kapal_params else 4.0))
    consumption = st.sidebar.number_input("Consumption (liter/jam)", value=safe(kapal_params.get('consumption') if kapal_params else 120))
    harga_bunker = st.sidebar.number_input("Harga Bunker (Rp/liter)", value=safe(kapal_params.get('harga_bunker') if kapal_params else 12500))
    harga_air_tawar = st.sidebar.number_input("Harga Air Tawar (Rp/Ton)", value=safe(kapal_params.get('harga_air_tawar') if kapal_params else 120000))
    port_cost = st.sidebar.number_input("Port cost/call (Rp)", value=safe(kapal_params.get('port_cost') if kapal_params else 50000000))
    asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=safe(kapal_params.get('asist_tug') if kapal_params else 35000000))
    premi_nm = st.sidebar.number_input("Premi (Rp/NM)", value=safe(kapal_params.get('premi_nm') if kapal_params else 50000))

    mode = st.radio("Pilih Mode Biaya:", ["Owner", "Charter"])

    if mode == "Owner":
        angsuran = st.sidebar.number_input("Angsuran (Rp/bulan)", value=safe(kapal_params.get('angsuran') if kapal_params else 750000000))
        crew_cost = st.sidebar.number_input("Crew Cost (Rp/bulan)", value=safe(kapal_params.get('crew_cost') if kapal_params else 60000000))
        asuransi = st.sidebar.number_input("Asuransi (Rp/bulan)", value=safe(kapal_params.get('asuransi') if kapal_params else 50000000))
        docking = st.sidebar.number_input("Docking (Rp/bulan)", value=safe(kapal_params.get('docking') if kapal_params else 50000000))
        perawatan = st.sidebar.number_input("Perawatan (Rp/bulan)", value=safe(kapal_params.get('perawatan') if kapal_params else 50000000))
        sertifikat = st.sidebar.number_input("Sertifikat (Rp/bulan)", value=safe(kapal_params.get('sertifikat') if kapal_params else 50000000))
        depresiasi = st.sidebar.number_input("Depresiasi (Rp/Beli)", value=safe(kapal_params.get('depresiasi') if kapal_params else 45000000000))
        other_cost = st.sidebar.number_input("Other Cost (Rp)", value=safe(kapal_params.get('other_cost') if kapal_params else 50000000))
    else:
        charter_hire = st.sidebar.number_input("Charter Hire (Rp/bulan)", value=safe(kapal_params.get('charter_hire') if kapal_params else 750000000))
        other_cost = st.sidebar.number_input("Other Cost (Rp)", value=safe(kapal_params.get('other_cost') if kapal_params else 50000000))

    port_stay = st.sidebar.number_input("Port Stay (Hari)", value=safe(kapal_params.get('port_stay') if kapal_params else 10))

    st.sidebar.markdown("---")
    # Save current sidebar parameters as kapal
    with st.sidebar.expander("💾 Simpan parameter ini sebagai Kapal baru"):
        new_kapal_name = st.text_input("Nama Kapal baru", value="")
        if st.button("Simpan Kapal Baru"):
            if not new_kapal_name.strip():
                st.error("Nama kapal wajib diisi!")
            else:
                data = {
                    'nama_kapal': new_kapal_name.strip(),
                    'speed_kosong': speed_kosong,
                    'speed_isi': speed_isi,
                    'consumption': consumption,
                    'harga_bunker': harga_bunker,
                    'harga_air_tawar': harga_air_tawar,
                    'port_cost': port_cost,
                    'asist_tug': asist_tug,
                    'premi_nm': premi_nm,
                    'angsuran': angsuran if mode == 'Owner' else None,
                    'crew_cost': crew_cost if mode == 'Owner' else None,
                    'asuransi': asuransi if mode == 'Owner' else None,
                    'docking': docking if mode == 'Owner' else None,
                    'perawatan': perawatan if mode == 'Owner' else None,
                    'sertifikat': sertifikat if mode == 'Owner' else None,
                    'depresiasi': depresiasi if mode == 'Owner' else None,
                    'other_cost': other_cost,
                    'charter_hire': charter_hire if mode == 'Charter' else None,
                    'port_stay': port_stay
                }
                success, msg = tambah_kapal(data)
                if success:
                    st.success(msg)
                    st.experimental_rerun()
                else:
                    st.error(f"Gagal menyimpan: {msg}")

    st.sidebar.markdown("---")
    # Manage kapal (edit/delete)
    with st.sidebar.expander("🛠️ Manage Kapal (Edit / Hapus)"):
        if df_kapal.empty:
            st.info("Belum ada kapal tersimpan.")
        else:
            edit_choice = st.selectbox("Pilih Kapal untuk Edit/Hapus", df_kapal['nama_kapal'].tolist())
            if edit_choice:
                row = get_kapal_by_name(edit_choice)
                if row:
                    with st.form("edit_kapal_form"):
                        e_name = st.text_input("Nama Kapal", value=row['nama_kapal'])
                        e_speed_kosong = st.number_input("Speed Kosong (knot)", value=safe(row.get('speed_kosong')))
                        e_speed_isi = st.number_input("Speed Isi (knot)", value=safe(row.get('speed_isi')))
                        e_consumption = st.number_input("Consumption (liter/jam)", value=safe(row.get('consumption')))
                        e_harga_bunker = st.number_input("Harga Bunker (Rp/liter)", value=safe(row.get('harga_bunker')))
                        e_harga_air = st.number_input("Harga Air Tawar (Rp/Ton)", value=safe(row.get('harga_air_tawar')))
                        e_port_cost = st.number_input("Port cost/call (Rp)", value=safe(row.get('port_cost')))
                        submitted_edit = st.form_submit_button("Update Kapal")
                        if submitted_edit:
                            data_update = {
                                'nama_kapal': e_name.strip(),
                                'speed_kosong': e_speed_kosong,
                                'speed_isi': e_speed_isi,
                                'consumption': e_consumption,
                                'harga_bunker': e_harga_bunker,
                                'harga_air_tawar': e_harga_air,
                                'port_cost': e_port_cost
                            }
                            ok = update_kapal_by_id(row['id'], data_update)
                            if ok:
                                st.success("Data kapal diperbarui.")
                                st.experimental_rerun()
                            else:
                                st.error("Gagal update kapal.")
                    if st.button(f"Hapus kapal {row['nama_kapal']}"):
                        ok = hapus_kapal_by_id(row['id'])
                        if ok:
                            st.warning("Kapal dihapus.")
                            st.experimental_rerun()
                        else:
                            st.error("Gagal menghapus kapal.")

    # ==============================
    # Main Inputs (body)
    # ==============================
    st.header("📥 Input Utama")
    pol = st.text_input("Port of Loading (POL)")
    pod = st.text_input("Port of Discharge (POD)")
    total_cargo = st.number_input("Total Cargo (MT)", value=7500)
    jarak = st.number_input("Jarak (NM)", value=630)

    # ==============================
    # Perhitungan Dasar (gunakan params dari sidebar)
    # ==============================
    sailing_time = (jarak / (speed_kosong if speed_kosong>0 else 1)) + (jarak / (speed_isi if speed_isi>0 else 1))
    voyage_days = (sailing_time / 24) + port_stay
    total_consumption = (sailing_time * consumption) + (port_stay * consumption)

    # Biaya umum
    biaya_umum = {
        "Bunker BBM": total_consumption * harga_bunker,
        "Air Tawar": (voyage_days * 2) * harga_air_tawar,
        "Port Cost": port_cost * 2,
        "Premi": premi_nm * jarak,
        "Asist": asist_tug
    }

    # Biaya per Mode
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

    total_cost = sum(biaya_mode.values()) + sum(biaya_umum.values())
    cost_per_mt = total_cost / total_cargo if total_cargo>0 else 0

    biaya_mode_rp = {k: f"Rp {v:,.0f}" for k, v in biaya_mode.items()}
    biaya_umum_rp = {k: f"Rp {v:,.0f}" for k, v in biaya_umum.items()}

    # ==============================
    # Tampilkan Hasil
    # ==============================
    st.header("📊 Hasil Perhitungan")
    st.write(f"Sailing Time (jam): {sailing_time:,.2f}")
    st.write(f"Total Voyage Days: {voyage_days:,.2f}")
    st.write(f"Total Consumption (liter): {total_consumption:,.0f}")

    st.subheader(f"💰 Biaya Mode ({mode})")
    for k, v in biaya_mode_rp.items():
        st.write(f"- {k}: {v}")

    st.subheader("💰 Biaya Umum")
    for k, v in biaya_umum_rp.items():
        st.write(f"- {k}: {v}")

    st.subheader("🧮 Total Cost")
    st.write(f"TOTAL COST: Rp {total_cost:,.0f}")
    st.subheader("🧮 Cost per MT")
    st.write(f"FREIGHT: Rp {cost_per_mt:,.0f} / MT")

    # ==============================
    # Profit Scenario
    # ==============================
    st.subheader("📈 Freight dengan Profit (0% - 50%)")
    profit_list = []
    for p in range(0, 55, 5):
        freight = cost_per_mt * (1 + (p / 100))
        revenue = freight * total_cargo
        Pph = revenue * 0.012
        net_profit = revenue - Pph - total_cost
        profit_list.append([f"{p}%", f"Rp {freight:,.0f}", f"Rp {revenue:,.0f}", f"Rp {Pph:,.0f}", f"Rp {net_profit:,.0f}"])
    profit_df = pd.DataFrame(profit_list, columns=["Profit %", "Freight / MT", "Revenue", "Pph", "Net Profit"])
    st.table(profit_df)

    # ==============================
    # PDF Report
    # ==============================
    input_data = [
        ["POL", pol],
        ["POD", pod],
        ["Jarak (NM)", f"{jarak:,}"],
        ["Total Cargo (MT)", f"{total_cargo:,}"],
        ["Voyage Days", f"{voyage_days:,.2f} hari"],
    ]
    results = list(biaya_mode_rp.items()) + list(biaya_umum_rp.items())
    results.append(["TOTAL COST", f"Rp {total_cost:,.0f}"])
    results.append(["Cost per MT", f"Rp {cost_per_mt:,.0f} / MT"])

    def generate_pdf(input_data, results, profit_df):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
            leftMargin=60, rightMargin=50, topMargin=30, bottomMargin=40
        )
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("🚢 Laporan Freight Tongkang", styles["Title"]))
        elements.append(Paragraph("📥 Input Utama", styles["Heading2"]))
        table_input = Table(input_data, colWidths=[200, 200])
        table_input.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey), ("FONTSIZE", (0,0), (-1,-1), 9)]))
        elements.append(table_input)
        elements.append(Spacer(1,1))

        elements.append(Paragraph("📊 Hasil Perhitungan", styles["Heading2"]))
        table_results = Table(results, colWidths=[200, 200])
        table_results.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey), ("FONTSIZE", (0,0), (-1,-1), 9)]))
        elements.append(table_results)
        elements.append(Spacer(1,1))

        elements.append(Paragraph("📈 Skenario Profit (0% - 50%)", styles["Heading2"]))
        data_profit = [list(profit_df.columns)] + profit_df.values.tolist()
        table_profit = Table(data_profit, colWidths=[60,100,120,120,120])
        table_profit.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (1,1), (-1,-1), "RIGHT"),
            ("ALIGN", (0,1), (0,-1), "LEFT"),
            ("FONTSIZE", (0,0), (-1,-1), 9)
        ]))
        elements.append(table_profit)
        doc.build(elements)
        buffer.seek(0)
        return buffer

    pdf_buffer = generate_pdf(input_data, results, profit_df)

    st.download_button(
        label="📥 Download Laporan PDF",
        data=pdf_buffer,
        file_name=f"Freight_Report_{pol or 'POL'}_{pod or 'POD'}.pdf",
        mime="application/pdf"
    )

    # ==============================
    # Logout
    # ==============================
    st.sidebar.markdown("---")
    logout_btn = st.sidebar.button("Logout")
    if logout_btn:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

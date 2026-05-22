import streamlit as st
import pandas as pd
from io import BytesIO
from distance import *
from auth import *
from presets import *
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime
import base64
import requests
import json
import os
import uuid
from auth import login_user, register_user
import streamlit.components.v1 as components
from streamlit_cookies_manager import EncryptedCookieManager
from pdf_generator import create_pdf
from styles import load_css
from intro import show_intro
from admin_panel import show_admin_panel

cookies = EncryptedCookieManager(
    prefix="freight_app",
    password="abc123"
)

if not cookies.ready():
    st.stop()

# =========================
# 🔐 ADMIN CONTROL
# =========================
ADMIN_EMAIL = "Muhammadiqnaa@gmail.com"

def is_admin():
    email = st.session_state.get("email") or cookies.get("email")
    return email == ADMIN_EMAIL


# =========================
# 💾 SAVE FREIGHT INPUT HISTORY
# =========================
def save_input_history(pol, pod, cargo, qty, freight_input, freight_cost, fuel_price, email):

    url = "https://freight-calculator-2b823-default-rtdb.asia-southeast1.firebasedatabase.app/calculate_history.json"

    today = datetime.now().strftime("%Y-%m-%d")

    # 🔥 AMBIL DATA LAMA
    try:
        res = requests.get(url)
        existing_data = res.json()
    except:
        existing_data = None

    # 🔥 CEK DUPLICATE
    if existing_data:
        for item in existing_data.values():
            if (
                item.get("date") == today and
                item.get("pol") == pol and
                item.get("pod") == pod and
                item.get("email") == email
            ):
                # ❌ DUPLICATE → STOP SAVE
                return

    # ✅ KALAU TIDAK ADA → SAVE
    data = {
        "pol": pol,
        "pod": pod,
        "type_cargo": cargo,
        "qty": qty,
        "freight_input": freight_input,
        "freight_cost": freight_cost,
        "fuel_price": fuel_price,
        "date": today,
        "email": email }
    
    requests.post(url, json=data)
        

# ==========================================================
# ⚙️ Page Config (WAJIB paling atas!)
# ==========================================================
st.set_page_config(
    page_title="Freight Calculator Barge",
    page_icon="https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/icon-512x512.png",
    layout="wide"
)

load_css()

show_intro(cookies)


# ==========================================================
# 🔧 PWA Support — biar bisa di-install di HP
# ==========================================================
st.markdown("""
<link rel="manifest" href="https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/manifest.json">
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/service-worker.js')
    .then(reg => console.log("Service worker registered:", reg))
    .catch(err => console.log("Service worker failed:", err));
}
</script>
""", unsafe_allow_html=True)

# ==========================================================
# 🍎 iPhone (Safari) Support — tambahan meta
# ==========================================================
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="FreightCalc">
""", unsafe_allow_html=True)


# ✅ AUTO LOGIN DARI COOKIE (WAJIB DI ATAS)
if cookies.get("logged_in") == "true" and cookies.get("email"):
    st.session_state.logged_in = True
    st.session_state.email = cookies.get("email")

# 🔥 FORCE SYNC EMAIL (ANTI BUG ADMIN HILANG)
if st.session_state.get("email") is None:
    st.session_state.email = cookies.get("email")

if "page" not in st.session_state:
    st.session_state.page = "login"

if "register_success" not in st.session_state:
    st.session_state.register_success = False

# ===== SESSION INIT =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "show_register" not in st.session_state:
    st.session_state.show_register = False

if "email" not in st.session_state:
    st.session_state.email = ""

# ===== DELETE STATE INIT =====
if "delete_success" not in st.session_state:
    st.session_state.delete_success = False

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

if "last_route" not in st.session_state:
    st.session_state.last_route = ""


# ===== AUTH PAGE CONTROLLER =====
if not st.session_state.logged_in:

    # =========================
    # PAGE: LOGIN
    # =========================
    if st.session_state.page == "login":

        st.markdown("<h2 style='text-align:center;'>🔐 Login Freight Calculator Barge</h2>", unsafe_allow_html=True)
        
        if st.session_state.register_success:
            st.success("🎉 Registrasi berhasil! Silakan login untuk melanjutkan.")
            st.session_state.register_success = False

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("LOGIN", type="primary", use_container_width=True):
            ok, data = login_user(email, password)

            if ok:
                st.session_state.logged_in = True
                st.session_state.email = email
            
                cookies["logged_in"] = "true"
                cookies["email"] = email
                cookies.save()
            
                st.rerun()
            else:
                st.error(f"❌ {data}")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Create New Account", type="secondary", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

        st.stop()


    # =========================
    # PAGE: REGISTER
    # =========================
    if st.session_state.page == "register":

        st.markdown("<h2 style='text-align:center;'>🆕Create Account Freight Calculator Barge</h2>", unsafe_allow_html=True)

        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Create New Account", use_container_width=True):
            ok, data = register_user(reg_email, reg_password)

            if ok:
                st.session_state.register_success = True
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Register gagal")

        if st.button("← Back to Login"):
            st.session_state.page = "login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.stop()

# ==== PRESET SEGMEN ====

# Default state
if "preset_selected" not in st.session_state:
    st.session_state.preset_selected = "Custom"


def get_pods_by_pol(pol):
    data = load_distances()
    pol = (pol or "").strip().upper()

    pods = set()

    for route in data.keys():
        try:
            p, d = route.split(" - ")

            p = p.strip().upper()
            d = d.strip().upper()

            # ✅ normal direction
            if p == pol:
                pods.add(d)

            # 🔥 reverse direction (INI KUNCINYA)
            elif d == pol:
                pods.add(p)

        except:
            continue

    return sorted(list(pods))

def get_next_by_pod(pod):
    data = load_distances()
    pod = (pod or "").strip().upper()

    next_ports = set()

    for route in data.keys():
        try:
            p, d = route.split(" - ")

            p = p.strip().upper()
            d = d.strip().upper()

            # maju
            if p == pod:
                next_ports.add(d)

            # 🔥 balik
            elif d == pod:
                next_ports.add(p)

        except:
            continue

    return sorted(list(next_ports))


# ==== APPLY PRESET (ONLY ONCE) ====
if "preset_applied" not in st.session_state:
    st.session_state.preset_applied = False


def apply_preset():
    selected = st.session_state.get("preset_control")

    if selected not in preset_params:
        return

    chosen = preset_params.get(selected)
    if not chosen:
        return

    for k, v in chosen.items():
        st.session_state[k] = v

st.sidebar.markdown("### 🚢 Barge Class")

options = ["270 ft", "300 ft", "330 ft", "Custom"]

if "preset_control" not in st.session_state:
    st.session_state.preset_control = "270 ft"

cols = st.sidebar.columns(4)

for i, opt in enumerate(options):

    # 🔥 ACTIVE STYLE
    is_active = st.session_state.preset_control == opt

    if is_active:
        btn_type = "primary"
    else:
        btn_type = "secondary"

    if cols[i].button(
        opt,
        key=f"barge_{opt}",
        type=btn_type,
        use_container_width=True
    ):
        st.session_state.preset_control = opt
        st.rerun()
        
selected = st.session_state.preset_control

if selected in preset_params:
    for k, v in preset_params[selected].items():
        st.session_state[k] = v

st.session_state.preset_selected = st.session_state.preset_control


# ===== MODE =====
mode = st.sidebar.selectbox("Mode", ["Owner", "Charter"])
# ===== DEFAULT VARIABLE =====
crew = 0
insurance = 0
docking = 0
maintenance = 0
certificate = 0

with st.sidebar.expander("➕ Add Distance"):

    pol_new = st.text_input("POL", key="new_pol")
    pod_new = st.text_input("POD", key="new_pod")
    distance_new = st.number_input("Distance (NM)", min_value=0.0, key="new_distance")

    if st.button("💾 Save Distance"):

        if pol_new and pod_new and distance_new > 0:

            data = load_distances()

            key = f"{pol_new.upper()} - {pod_new.upper()}"

            if key in data:
                st.warning("⚠️ Route sudah ada!")
            else:
                data[key] = distance_new
                save_distances(data)

                st.success("✅ Distance berhasil disimpan!")
        else:
            st.error("❌ Semua field wajib diisi!")


with st.sidebar.expander("📋 Saved Distance"):

    data = load_distances()

    # ===== NOTIF (MUNCUL SETELAH DELETE) =====
    if st.session_state.delete_success:
        st.success("Distance berhasil dihapus 🚀")
        st.session_state.delete_success = False

    if not data:
        st.info("Belum ada data distance")

    else:
        routes = list(data.keys())

        selected_route = st.selectbox(
            "Pilih route",
            routes
        )

        # ===== RESET CONFIRM KALAU GANTI ROUTE =====
        if st.session_state.last_route != selected_route:
            st.session_state.confirm_delete = False
            st.session_state.last_route = selected_route

        st.caption(f"Distance: {data[selected_route]:,.0f} NM")

        # ===== STEP 1: BUTTON DELETE =====
        if not st.session_state.confirm_delete:
            if st.button("🗑️ Delete Distance", use_container_width=True):
                st.session_state.confirm_delete = True
                st.rerun()

        # ===== STEP 2: KONFIRMASI =====
        else:
            st.warning("⚠️ Yakin mau hapus data ini?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.confirm_delete = False
                    st.rerun()

            with col2:
                if st.button("✅ Confirm Delete", use_container_width=True):

                    del data[selected_route]
                    save_distances(data)

                    # 🔥 TRIGGER NOTIF
                    st.session_state.delete_success = True
                    st.session_state.confirm_delete = False

                    st.rerun()

# ===== SIDEBAR PARAMETERS =====
with st.sidebar.expander("⚙️ Operational Input", expanded=False):
    
    speed_laden = st.number_input(
        "Speed Laden (knot)",
        value=float(st.session_state.get("speed_laden", 0)),
        step=0.1,
        format="%.2f"
    )
    speed_ballast = st.number_input(
        "Speed Ballast (knot)",
        value=float(st.session_state.get("speed_ballast", 0)),
        step=0.1,
        format="%.2f"
    )
    weather_factor = st.number_input(
        "Weather Factor (%)",
        value=float(st.session_state.get("weather_factor", 5)),
        step=1.0
    )
    consumption = st.number_input("Fuel Consumption (L/hr)", value=st.session_state.get("consumption", 0))
    price_fuel = st.number_input("Fuel Price (Rp/L)", value=st.session_state.get("price_fuel", 0))

    consumption_fw = st.number_input("FW Consumption (Ton/Day)", value=st.session_state.get("consumption_fw", 0))
    price_fw = st.number_input("FW Price (Rp/Ton)", value=st.session_state.get("price_fw", 0))

if mode == "Owner":
    with st.sidebar.expander("🏗️ Cost (Owner)", expanded=False):
        charter = st.number_input("Angsuran (Rp/Month)", value=0)
        crew = st.number_input("Crew (Rp/Month)", value=st.session_state.get("crew", 0))
        insurance = st.number_input("Insurance (Rp/Month)", value=st.session_state.get("insurance", 0))
        docking = st.number_input("Docking (Rp/Month)", value=st.session_state.get("docking", 0))
        maintenance = st.number_input("Maintenance (Rp/Month)", value=st.session_state.get("maintenance", 0))
        certificate = st.number_input("Certificate (Rp/Month)", value=st.session_state.get("certificate", 0))
        premi_nm = st.number_input("Premi (Rp/NM)", value=st.session_state.get("premi_nm", 0))
        other_cost = st.number_input("Other Cost (Rp)", value=st.session_state.get("other_cost", 0))
else:
    with st.sidebar.expander("🏗️ Cost (Charter)", expanded=False):
        charter = st.number_input("Charter Hire (Rp/Month)", value=st.session_state.get("charter", 0))
        premi_nm = st.number_input("Premi (Rp/NM)", value=st.session_state.get("premi_nm", 0))
        other_cost = st.number_input("Other Cost (Rp)", value=st.session_state.get("other_cost", 0))

with st.sidebar.expander("⚓ Port Cost"):
    port_cost_pol = st.number_input("Port Cost POL (Rp)", value=st.session_state.get("port_cost_pol", 0))
    port_cost_pod = st.number_input("Port Cost POD (Rp)", value=st.session_state.get("port_cost_pod", 0))
    asist_tug = st.number_input("Asist Tug (Rp)", value=st.session_state.get("asist_tug", 0))

with st.sidebar.expander("🏢 General Overhead"):
    opex_office = st.number_input(
        "Opex (Rp/Month)",
        value=st.session_state.get("opex_office", 0)
    )
    depreciation_kapal = st.number_input(
        "Depreciation Kapal (Rp/Month)",
        value=st.session_state.get("depreciation_kapal", 0)
    )

with st.sidebar.expander("🕓 Port Stay"):
    port_stay_pol = st.number_input("POL (Days)", value=st.session_state.get("port_stay_pol", 0))
    port_stay_pod = st.number_input("POD (Days)", value=st.session_state.get("port_stay_pod", 0))

# ===== ADDITIONAL COST =====
with st.sidebar.expander("➕ Additional Cost"):
    if "additional_costs" not in st.session_state:
        st.session_state.additional_costs = []

    add_new = st.button("➕ Add Additional Cost")
    if add_new:
        st.session_state.additional_costs.append({
            "name": "",
            "price": 0,
            "unit": "Ltr",
            "subtype": "Day",
            "consumption": 0
        })

    updated_costs = []
    unit_options = ["Ltr", "Ton", "Month", "Voyage", "MT", "M3", "Day"]

    for i, cost in enumerate(st.session_state.additional_costs):
        st.markdown(f"**Additional Cost {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"Name {i+1}", cost.get("name", ""), key=f"name_{i}")
            price = st.number_input(f"Price {i+1} (Rp)", cost.get("price", 0), key=f"price_{i}")
        with col2:
            unit = st.selectbox(
                f"Unit {i+1}",
                unit_options,
                index=unit_options.index(cost.get("unit", "Ltr")) if cost.get("unit", "Ltr") in unit_options else 0,
                key=f"unit_{i}"
            )
            subtype = "Day"
            if unit in ["Ltr", "Ton"]:
                subtype = st.selectbox(
                    f"Type {i+1}",
                    ["Day", "Hour"],
                    index=["Day", "Hour"].index(cost.get("subtype", "Day")),
                    key=f"subtype_{i}"
                )
            additional_consumption = 0
            if unit in ["Ltr", "Ton"]:
                additional_consumption = st.number_input(
                    f"Consumption {i+1} ({unit}/{subtype})",
                    cost.get("consumption", 0),
                    key=f"additional_consumption_{i}"
                )

        remove = st.button(f"❌ Remove {i+1}", key=f"remove_{i}")
        if not remove:
            updated_costs.append({
                "name": name,
                "price": price,
                "unit": unit,
                "subtype": subtype,
                "consumption": additional_consumption
            })
    st.session_state.additional_costs = updated_costs
    
if is_admin():
    show_admin_panel()
            
# ===== LOGOUT =====
st.sidebar.markdown("### Account")
st.sidebar.write(f"**{st.session_state.email}**")
if st.sidebar.button("**Log Out**"):
    st.session_state.logged_in = False
    st.session_state.page = "login"

    st.session_state.hide_intro = False
    cookies["hide_intro"] = "false"

    cookies["logged_in"] = "false"
    cookies.pop("email", None)

    cookies.save()

    st.success("Successfully logged out.")
    st.rerun()

# ===== HEADER WITH INFO BUTTON =====
col1, col2 = st.columns([9,1])

with col1:
    st.markdown("""
    <div style="
        width: 100%;
        background: linear-gradient(135deg, #6495ED, #FFFFFF, #6495ED);
        padding: 20px 14px;
        border-radius: 16px;
        text-align: center;
        color: Black;
        margin-bottom: 10px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.45);
    ">
    <div style="
            font-size: 35px;
            font-weight: 900;
    ">
            🚢 Freight Calculator
    </div>

    <div style="
            font-size: 12px;
            margin-top: 6px;
            color: #64748B;
    ">
            Shipping Cost & Profit Tool
    </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if "show_info" not in st.session_state:
        st.session_state.show_info = False

    if st.button("ℹ️", help="Info & Tutorial", use_container_width=True):
        st.session_state.show_info = not st.session_state.show_info


# ===== POPUP INFO SAFE VERSION =====
if st.session_state.show_info:

    # ✅ CEK: apakah st.modal tersedia
    if hasattr(st, "modal"):

        with st.modal("ℹ️ Info & Tutorial"):

            tab1, tab2 = st.tabs(["📊 Tentang", "📘 Cara Pakai"])

            with tab1:
                st.markdown("""
                ### 🚢 Freight Calculator Barge

                Aplikasi untuk menghitung:
                • Total biaya voyage  
                • Freight per ton  
                • Profit / loss  
                • TCE  
                """)

            with tab2:
                st.markdown("""
                ### 📘 Cara Pakai

                1. Pilih Barge Class
                2. Pilih POL & POD
                3. Isi cargo & freight
                4. Klik CALCULATE
                """)

    # ❌ kalau modal tidak ada → pakai fallback
    else:

        st.markdown("## ℹ️ Info & Tutorial")

        tab1, tab2, tab3 = st.tabs(["📊 Tentang", "📘 Cara Pakai", "⚠️ Catatan"])

        with tab1:
            st.markdown("""
            ### 🚢 Freight Calculator Barge
        
            Aplikasi ini adalah tools untuk menghitung **biaya operasional kapal tongkang (barge)** secara otomatis berdasarkan rute, cargo, dan parameter kapal.
        
            ---
        
            ### 🎯 Fungsi Utama:
            - Menghitung total voyage cost (biaya perjalanan kapal)
            - Menghitung freight cost per MT / M³
            - Analisa profit / loss berdasarkan freight rate
            - Menghitung TCE (Time Charter Equivalent)
            - Simulasi beberapa skenario profit
        
            ---
        
            ### ⚙️ Parameter yang digunakan:
            - Speed laden & ballast  
            - Fuel consumption & harga fuel  
            - Fresh water consumption  
            - Port cost (POL & POD)  
            - Crew, insurance, maintenance  
            - Additional cost (custom input)  
            - Cargo quantity & jenis cargo  
        
            ---
        
            ### 📄 Output aplikasi:
            - Total cost voyage  
            - Freight cost per unit  
            - Profit & margin  
            - Breakdown cost detail  
            - PDF report otomatis  
            """)

        with tab2:
            st.markdown("""
            ### 📘 Cara Menggunakan Aplikasi
        
            Ikuti langkah berikut agar hasil perhitungan akurat:
        
            ---
        
            ### 1. Pilih Barge Class
            - 270 ft / 300 ft / 330 ft / Custom  
            - Ini akan otomatis mengisi parameter standar kapal  
        
            ---
        
            ### 2. Tentukan Rute
            - Pilih Loading Port (POL)  
            - Pilih Discharge Port (POD)  
            - Distance akan otomatis muncul jika tersedia  
        
            ---
        
            ### 3. Input Cargo
            - Pilih jenis cargo:
              - Coal (MT)
              - Nickel (MT)
              - Bauxite (MT)
              - Sand / Split (M³)
            - Masukkan quantity sesuai kebutuhan  
        
            ---
        
            ### 4. Input Freight Rate
            - Masukkan harga freight (Rp per MT)
            - Digunakan untuk simulasi revenue & profit  
        
            ---
        
            ### 5. Klik CALCULATE
            Sistem akan menghitung:
            - Total voyage cost
            - Fuel & freshwater cost
            - Port cost & operational cost
            - Profit / loss
            - TCE (per day & per month)
        
            ---
        
            ### 6. Download Report (PDF)
            - Hasil bisa langsung di-download
            - Cocok untuk:
              - Negotiation
              - Reporting
              - Analisa voyage
            """)


        with tab3:
            st.markdown("""
            ### ⚠️ Catatan Penting
        
            - Data distance harus tersedia agar otomatis terisi  
            - Jika tidak ada, bisa input manual di Add Distance
            - Parameter bisa di edit sesuai biaya akurat
            - Semua hasil adalah simulasi berdasarkan input user  
            - Gunakan data real untuk hasil lebih akurat  
            - Aplikasi ini untuk analisa & perencanaan voyage  
            """)
                    

        if st.button("❌ Tutup"):
            st.session_state.show_info = False
            st.rerun()
            

# ===== MAIN INPUT =====
st.markdown("### 🚢 Voyage Input")

# ===== POL =====
all_ports = get_all_ports()

port_pol = st.selectbox("Loading Port (POL)", [""] + all_ports)

# ===== POD (muncul setelah POL dipilih) =====
if port_pol:
    pods = get_pods_by_pol(port_pol)
    port_pod = st.selectbox("Discharge Port (POD)", [""] + pods)
else:
    port_pod = ""

# ===== NEXT PORT (muncul setelah POD dipilih) =====
if port_pod:
    next_ports = get_next_by_pod(port_pod)
    next_port = st.selectbox("Next Port (Optional)", [""] + next_ports)
else:
    next_port = ""

st.markdown("### 📏 Distance")

col1, col2 = st.columns(2)

with col1:
    if port_pol and port_pod:
        auto_distance = find_distance(port_pol, port_pod)
    else:
        auto_distance = 0

    st.text_input("POL → POD (NM)", value=str(auto_distance), disabled=True)

with col2:
        # hanya hitung kalau NEXT PORT dipilih
        if port_pod and next_port:
            auto_distance_return = find_distance(port_pod, next_port)
            st.text_input("POD → NEXT (NM)", value=str(auto_distance_return), disabled=True)

st.markdown("### 📦 Type Cargo & Quantity")

col1, col2 = st.columns(2)

# ===== TYPE CARGO =====
with col1:
    type_cargo = st.selectbox(
        "Type",
        ["Bauxite (MT)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)", "Palm kernel (MT)"],
        key="type_cargo",
        label_visibility="collapsed"
    )

# ===== DEFAULT QTY =====
default_qty = 0
if st.session_state.preset_selected in cargo_qty_default:
    default_qty = cargo_qty_default[st.session_state.preset_selected].get(type_cargo, 0)

# ===== INIT =====
if "qyt_cargo" not in st.session_state:
    st.session_state.qyt_cargo = default_qty

# ===== AUTO UPDATE =====
if (
    "last_preset" not in st.session_state or
    "last_cargo" not in st.session_state or
    st.session_state.last_preset != st.session_state.preset_selected or
    st.session_state.last_cargo != type_cargo
):
    st.session_state.qyt_cargo = default_qty

st.session_state.last_preset = st.session_state.preset_selected
st.session_state.last_cargo = type_cargo

# ===== QTY =====
with col2:
    unit = type_cargo.split("(")[-1].replace(")", "")

    qyt_cargo = st.number_input(
        f"Qty ({unit})",
        value=st.session_state.qyt_cargo,
        key="qyt_cargo",
        label_visibility="collapsed"
    )

st.markdown("### 💰 Budget Shipper")

col_mode, col_input = st.columns([1, 3])

with col_mode:
    freight_mode = st.selectbox(
        "Mode",
        ["Freight Rate / MT", "Lump Sum"],
        label_visibility="collapsed"
    )

with col_input:
    if freight_mode == "Freight Rate / MT":
        freight_price_input = st.number_input(
            "Input Freight",
            min_value=0.0,
            step=1000.0,
            label_visibility="collapsed"
        )
    else:
        freight_price_input = st.number_input(
            "Input Lump Sum",
            min_value=0.0,
            step=1000000.0,
            label_visibility="collapsed"
        )

# ===== NOTE =====
if freight_mode == "Freight Rate / MT":
    st.caption("📌 Freight dihitung berdasarkan quantity cargo × freight rate per MT")
else:
    st.caption("📌 Freight menggunakan total nilai tetap (lump sum freight)")

st.markdown("### 🎯 Target Profit")

col_mode, col_input = st.columns([1, 3])

with col_mode:
    margin_type = st.selectbox(
        "Mode",
        ["%", "Rp"],
        label_visibility="collapsed"
    )

with col_input:
    target_margin = st.number_input(
        "Input",
        min_value=0.0,
        step=0.1,
        label_visibility="collapsed"
    )

if margin_type == "%":
    st.caption("📌 Mode % = Target profit dihitung dari Freight Cost dengan persen")
else:
    st.caption("📌 Mode Rp = Target profit dihitung dari Freight Cost dengan nominal")

if not port_pol or not port_pod:
    st.error("⚠️ Pilih POL & POD")
    st.stop()

# ===== BUTTON =====
st.markdown("<br>", unsafe_allow_html=True)

calculate = st.button(
    "**🚀 CALCULATE NOW**",
    use_container_width=True,
    type="primary"
)


# ===== PERHITUNGAN =====

if calculate:
    try:
        distance_pol_pod = find_distance(port_pol, port_pod)

        # 🔥 FIX: hanya hitung kalau NEXT PORT dipilih
        if next_port and next_port.strip():
            distance_pod_pol = find_distance(port_pod, next_port)
        else:
            distance_pod_pol = 0

        pol_pod_hour = distance_pol_pod / speed_laden if speed_laden else 0
        pod_pol_hour = distance_pod_pol / speed_ballast if speed_ballast else 0

        # ===== SAILING TIME =====
        base_sailing_time = (
            (distance_pol_pod / speed_laden if speed_laden else 0)
            + (distance_pod_pol / speed_ballast if speed_ballast else 0)
        )

        # ===== WEATHER FACTOR =====
        weather_delay = base_sailing_time * (weather_factor / 100)

        # ===== FINAL SAILING TIME =====
        sailing_time = base_sailing_time + weather_delay

        # ===== DAY CONVERSION =====
        pol_pod_day = pol_pod_hour / 24
        pod_pol_day = pod_pol_hour / 24

        # ===== TOTAL VOYAGE =====
        total_voyage_days = (
            (sailing_time / 24)
            + (port_stay_pol + port_stay_pod)
        )

        total_voyage_days_round = (
            int(total_voyage_days)
            if total_voyage_days % 1 < 0.5
            else int(total_voyage_days) + 1
        )

        # ===== CONSUMPTION =====
        total_consumption_fuel = (
            (sailing_time * consumption)
            + ((port_stay_pol + port_stay_pod) * 120)
        )

        total_consumption_fw = (
            consumption_fw * total_voyage_days_round
        )

        cost_fw = total_consumption_fw * price_fw
        cost_fuel = total_consumption_fuel * price_fuel
        
        # core costs
        charter_cost = (charter / 30) * total_voyage_days
        crew_cost = (crew / 30) * total_voyage_days if mode == "Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode == "Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode == "Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode == "Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode == "Owner" else 0
        total_general_overhead = (opex_office / 30) * total_voyage_days
        depreciation_cost = (depreciation_kapal / 30) * total_voyage_days
        premi_cost = distance_pol_pod * premi_nm
        port_cost = port_cost_pol + port_cost_pod + asist_tug

        # ===== COST DICTIONARY =====
        if mode == "Owner":
            owner_data = {
                "Angsuran": charter_cost,
                "Crew": crew_cost,
                "Insurance": insurance_cost,
                "Docking": docking_cost,
                "Maintenance": maintenance_cost,
                "Certificate": certificate_cost,
                "Premi": premi_cost,
                "Port Costs": port_cost,
                "Other Cost": other_cost
            }
        else:
            owner_data = {
                "Charter Hire": charter_cost,
                "Premi": premi_cost,
                "Port Costs": port_cost,
                "Other Cost": other_cost
            }

        # ===== ADDITIONAL COST CALCULATION =====
        additional_total = 0
        additional_breakdown = {}

        for cost in st.session_state.get("additional_costs", []):
            name = cost.get("name", "")
            unit = cost.get("unit", "")
            subtype = cost.get("subtype", "Day")
            price = cost.get("price", 0)
            cons = cost.get("consumption", 0)

            val = 0
            if unit == "Ltr":
                if subtype == "Day":
                    val = cons * total_voyage_days * price
                elif subtype == "Hour":
                    val = cons * (total_voyage_days * 24) * price
            elif unit == "Ton":
                if subtype == "Day":
                    val = cons * total_voyage_days * price
                elif subtype == "Hour":
                    val = cons * (total_voyage_days * 24) * price
            elif unit == "Month":
                val = (price / 30) * total_voyage_days
            elif unit == "Voyage":
                val = price
            elif unit in ["MT", "M3"]:
                val = price * qyt_cargo
            elif unit == "Day":
                val = price * total_voyage_days

            if val and val > 0:
                key_name = name if name else f"{unit} cost"
                if key_name in additional_breakdown:
                    additional_breakdown[key_name] += val
                else:
                    additional_breakdown[key_name] = val
                additional_total += val

        # ===== TOTAL COST FINAL =====
        total_cost = sum([
            charter_cost, crew_cost, insurance_cost, docking_cost, maintenance_cost, certificate_cost,total_general_overhead,depreciation_cost, 
            premi_cost, port_cost, cost_fuel, cost_fw, other_cost, additional_total
        ])

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # ===== REVENUE CALC =====
        if freight_mode == "Freight Rate / MT":
            revenue_user = freight_price_input * qyt_cargo
        else:
            revenue_user = freight_price_input
        pph_user = revenue_user * 0.012
        profit_user = revenue_user - total_cost - pph_user
        profit_percent_user = (profit_user / total_cost * 100) if total_cost > 0 else 0

        # ===== REKOMENDASI FREIGHT =====
        if margin_type == "%":
            ideal_freight = freight_cost_mt * (1 + target_margin / 100)
        else:
            ideal_freight = freight_cost_mt + target_margin

        # ===== SAVE COST =====
        save_cost = (
            certificate_cost
            + docking_cost
            + insurance_cost
            + maintenance_cost
        )

        # ===== TCE CALCULATION =====
        tce_base_cost = cost_fuel + cost_fw + port_cost + premi_cost

        tce_per_day = (
            tce_base_cost / total_voyage_days
            if total_voyage_days > 0 else 0
        )

        tce_per_month = tce_per_day * 30

        # ===== SAVE HISTORY =====
        save_input_history(
            pol=port_pol,
            pod=port_pod,
            cargo=type_cargo,
            qty=qyt_cargo,
            freight_input=freight_price_input,
            freight_cost=freight_cost_mt,
            fuel_price=price_fuel,
            email=st.session_state.email
        )

        # ===== OUTPUT RINGKAS (MOBILE FRIENDLY) =====
        
        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg, #f8fafc, #eef5ff);
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            color:#0f172a;
            border-left:5px solid #93c5fd;
            box-shadow:0 4px 12px rgba(0,0,0,0.4);
        ">

        <h4 style="color:#93c5fd;"> 🚢 Voyage Summary </h4>

        • Cargo Type : <b>{type_cargo}</b><br>
        • Total Cargo : <b>{qyt_cargo:,.0f} {unit}</b><br>
        • Route : <b>{port_pol} → {port_pod} → {" - " + next_port if next_port else ""}</b><br>
        • Distance : <b>{distance_pol_pod:,.0f} NM</b><br>
        • Total Voyage : <b>{total_voyage_days:.1f} Days</b><br>
        • Freight Cost : 
        <b style="color:#2563eb;">
        Rp {freight_cost_mt:,.0f}/{unit}
        </b><br>
        <span style="color:#64748b;">
        (Save Cost : Rp {save_cost:,.0f})
        </span><br>

        {
        f'''• Rekomendasi Freight : 
        <b style="color:#16a34a;">
        Rp {ideal_freight:,.0f}/{unit}
        </b><br>'''
        if float(target_margin or 0) > 0 else ""
        }
        
        <hr style="margin:6px 0; opacity:0.15;">
        
        <div style="color:#64748b;">
        
        <b>Note :</b><br>
        • Fuel Price : Rp {price_fuel:,.0f}/Ltr<br>
        • Sailing POL → POD : {pol_pod_day:.1f} Days<br>
        • Sailing POD → POL : {pod_pol_day:.1f} Days<br>
        • Weather Factor : {weather_factor:.0f}%<br>
        • Save Cost : Insurance, Docking, Maintenance, Certificate<br>
        • Freight Cost based on Total Cost Calculation

    
        </div>
        """, unsafe_allow_html=True)
            
        if freight_price_input > 0:

            profit_color = "#16a34a" if profit_user >= 0 else "#dc2626"
            status = "PROFIT ✅" if profit_user >= 0 else "LOSS ❌"

            st.markdown(f"""
            <div style="
                background:linear-gradient(135deg, #f0fdf4, #ecfdf5);
                padding:12px;
                border-radius:12px;
                margin-bottom:10px;
                color:#052e16;
                border-left:5px solid {profit_color};
                box-shadow:0 4px 12px rgba(0,0,0,0.35);
            ">
            <h4 style="color:{profit_color};">💼 Budget Customer</h4>

            • Freight Input User: <b>Rp {freight_price_input:,.0f} / {type_cargo.split()[1]}</b><br>
            • Revenue: <b>Rp {revenue_user:,.0f}</b><br>
            • PPH 1.2%: <b>Rp {pph_user:,.0f}</b><br>
            • Total Cost : <b>Rp {total_cost:,.0f}</b><br>
            • Profit: <b style="color:{profit_color};">Rp {profit_user:,.0f} ({profit_percent_user:.2f}%)</b><br>
            • Status: <b style="color:{profit_color};">{status}</b>

            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg, #fff7ed, #fffbeb);
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            color:#0f172a;
            border-left:5px solid #f97316;
            box-shadow:0 4px 12px rgba(0,0,0,0.2);
        ">

        <h4 style="color:#f97316;">⛽ Variable Cost</h4>

        • Fuel Cost : <b>Rp {cost_fuel:,.0f}</b> ({total_consumption_fuel:,.0f} Ltr)<br>
        • FW Cost : <b>Rp {cost_fw:,.0f}</b> ({total_consumption_fw:,.0f} Ton)<br>
        • Premi : <b>Rp {premi_cost:,.0f}</b><br>
        • Port Cost : <b>Rp {port_cost:,.0f}</b><br>

        <hr style="margin:2px 0; opacity:0.2;">

        <b>Total Variable Cost :</b> 
        <b>Rp {(cost_fuel + cost_fw + premi_cost + port_cost):,.0f}</b>

        </div>
        """, unsafe_allow_html=True)
        
        # ===== OWNER / CHARTER TOTAL =====
        if mode == "Owner":
            owner_total = (
                charter_cost +
                crew_cost +
                insurance_cost +
                docking_cost +
                maintenance_cost +
                certificate_cost
            )
        else:
            owner_total = charter_cost
        
        
        # ===== TAMPILAN =====
        if mode == "Owner":
        
            st.markdown(f"""
            <div style="
            background:linear-gradient(135deg, #f5f3ff, #ede9fe);
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            border-left:5px solid #7c3aed;
            ">
            <h4 style="color:#7c3aed;">🏗️ Owner Cost</h4>
            • Installment : <b>Rp {charter_cost:,.0f}</b><br>
            • Crew : <b>Rp {crew_cost:,.0f}</b><br>
            • Insurance : <b>Rp {insurance_cost:,.0f}</b><br>
            • Docking : <b>Rp {docking_cost:,.0f}</b><br>
            • Maintenance : <b>Rp {maintenance_cost:,.0f}</b><br>
            • Certificate : <b>Rp {certificate_cost:,.0f}</b><br>
            <hr style="margin:2px 0; opacity:0.2;">
            <b>Total : Rp {owner_total:,.0f}</b>
            </div>
            """, unsafe_allow_html=True)
        
        else:
        
            st.markdown(f"""
            <div style="
            background:linear-gradient(135deg, #f5f3ff, #ede9fe);
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            border-left:5px solid #7c3aed;
            ">
            <h4 style="color:#7c3aed;">🏗️ Charter Cost</h4>
            • Charter Hire : <b>Rp {charter_cost:,.0f}</b><br>
            <hr style="margin:2px 0; opacity:0.2;">
            <b>Total : Rp {owner_total:,.0f}</b>
            </div>
            """, unsafe_allow_html=True)
    

        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg, #f8fafc, #f1f5f9);
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            border-left:5px solid #64748b;
        ">
        <h4 style="color:#64748b;">🏢 General & Administrative Cost (G&A)</h4>
        
        • General Overhead : <b>Rp {total_general_overhead:,.0f}</b><br>
        • Depreciation Kapal : <b>Rp {depreciation_cost:,.0f}</b><br>
        • Other Cost : <b>Rp {other_cost:,.0f}</b><br>
        
        <hr style="margin:2px 0; opacity:0.2;">
        
        <b>Total Opex : Rp {(total_general_overhead + depreciation_cost + other_cost):,.0f}</b>
        </div>
        """, unsafe_allow_html=True)

        if additional_breakdown:

            add_total = sum(additional_breakdown.values())

            items_html = ""
        
            for k, v in additional_breakdown.items():
                items_html += f"""
            <div style="margin-bottom:4px;">
                    • {k} : <b>Rp {v:,.0f}</b>
            </div>
            """
        
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #fdf2f8, #ffffff);
                padding:12px;
                border-radius:12px;
                margin-bottom:10px;
                border-left:5px solid #ec4899;
                box-shadow:0 4px 12px rgba(0,0,0,0.08);
                color:#0f172a;
            ">
            <h4 style="color:#ec4899;">➕ Additional Cost</h4>
        
            {items_html}
        
            <hr style="margin:2px 0; opacity:0.2;">
            
            <b>Total Additional Cost : Rp {add_total:,.0f}</b>
            </div>
            """, unsafe_allow_html=True)
            

        variable_total = cost_fuel + cost_fw + premi_cost + port_cost
        opex_total = total_general_overhead + depreciation_cost + other_cost
        additional_total = sum(additional_breakdown.values()) if additional_breakdown else 0

        summary_total = total_cost
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #eff6ff, #ffffff);
            padding:16px;
            border-radius:14px;
            margin-bottom:10px;
            color:#0f172a;
            border-left:5px solid #2563eb;
            box-shadow:0 6px 16px rgba(0,0,0,0.08);
        ">
        <h4 style="color:#2563eb;">📊 Summary Cost</h4>
        
        • Variable Cost : <b>Rp {variable_total:,.0f}</b><br>
        • Owner/Charter : <b>Rp {owner_total:,.0f}</b><br>
        • Opex Cost : <b>Rp {opex_total:,.0f}</b><br>
        • Additional Cost : <b>Rp {additional_total:,.0f}</b><br>
        
        <hr style="margin:2px 0; opacity:0.2;">
        
        <h3 style="margin:0; color:#0f172a;">
            Total : Rp {summary_total:,.0f}
        </h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg, #f8fafc, #eef5ff);
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            color:black;
            border-left:5px solid #03a9f4;
            box-shadow:0 4px 12px rgba(0,0,0,0.4);
        ">
        <h4 style="color:#03a9f4;">⏱️ TCE (Time Charter Equivalent)</h4>

        • Per Day: <b>Rp {tce_per_day:,.0f}</b><br>
        • Per Month: <b>Rp {tce_per_month:,.0f}</b>

        </div>
        """, unsafe_allow_html=True)


        # ===== PROFIT SCENARIO =====
        data = []
        for p in range(0, 80, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            gross_profit = revenue - total_cost - pph
            data.append([f"{p}%", f"Rp {freight_persen:,.0f}", f"Rp {revenue:,.0f}", f"Rp {pph:,.0f}", f"Rp {gross_profit:,.0f}"])
        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Gross Profit (Rp)"])

        st.subheader("💹 Profit Scenario 0–75%")
        st.dataframe(df_profit, use_container_width=True, height=250)


        # ===== GENERATE PDF & DOWNLOAD BUTTON =====
        pdf_buffer = create_pdf({

            "username": st.session_state.email,
        
            "port_pol": port_pol,
            "port_pod": port_pod,
            "next_port": next_port,
        
            "qyt_cargo": qyt_cargo,
            "type_cargo": type_cargo,
        
            "distance_pol_pod": distance_pol_pod,
            "total_voyage_days": total_voyage_days,
        
            "sailing_time": sailing_time,
        
            "total_consumption_fuel": total_consumption_fuel,
            "total_consumption_fw": total_consumption_fw,
        
            "cost_fuel": cost_fuel,
            "cost_fw": cost_fw,
        
            "total_general_overhead": total_general_overhead,
        
            "owner_data": owner_data,
            "additional_breakdown": additional_breakdown,
        
            "total_cost": total_cost,
            "freight_cost_mt": freight_cost_mt,
        
            "freight_price_input": freight_price_input,
            "freight_mode": freight_mode,
            "revenue_user": revenue_user,
            "pph_user": pph_user,
            "profit_user": profit_user,
            "profit_percent_user": profit_percent_user,
        
            "tce_base_cost": tce_base_cost,
            "tce_per_day": tce_per_day,
            "tce_per_month": tce_per_month,
        
            "df_profit": df_profit,

            "note": True,  # <- ini pemicu tampilkan note

            "fuel_price": price_fuel,
            "port_stay_pol": port_stay_pol,
            "port_stay_pod": port_stay_pod,
            "speed_laden": speed_laden,
            "speed_ballast": speed_ballast,
            "weather_factor": weather_factor,
            
        })
        selected_barge = st.session_state.get("preset_selected", "Custom")
        file_name = f"Freight Report {selected_barge} {port_pol}-{port_pod} ({datetime.now():%d%m%Y}).pdf"

        profit_rows = []

        for p in range(0, 80, 5):
        
            freight_value = freight_cost_mt * (1 + p / 100)
        
            revenue_value = freight_value * qyt_cargo
        
            pph_value = revenue_value * 0.012
        
            gross_profit = revenue_value - pph_value - total_cost
        
            profit_rows.append([
                f"{p}%",
                f"Rp {freight_value:,.0f}",
                f"Rp {revenue_value:,.0f}",
                f"Rp {pph_value:,.0f}",
                f"Rp {gross_profit:,.0f}",
            ])
        
        df_profit = pd.DataFrame(profit_rows, columns=[
            "Profit %",
            "Freight (Rp)",
            "Revenue (Rp)",
            "PPH 1.2% (Rp)",
            "Gross Profit (Rp)"
        ])

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")


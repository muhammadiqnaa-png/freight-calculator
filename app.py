import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime
import requests
import json
import os
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(
    prefix="freight_app",
    password="abc123"
)

if not cookies.ready():
    st.stop()

# ===== INTRO STATE =====
if "hide_intro" not in st.session_state:
    st.session_state.hide_intro = False

# ambil dari cookies (persist)
if cookies.get("hide_intro") == "true":
    st.session_state.hide_intro = True

DATA_FILE = "distance_data.json"

def find_distance(pol, pod):
    data = load_distances()

    pol = (pol or "").strip().upper()
    pod = (pod or "").strip().upper()

    for route, distance in data.items():
        try:
            p, d = route.split(" - ")

            p = p.strip().upper()
            d = d.strip().upper()

            # ✅ normal match
            if p == pol and d == pod:
                return distance

            # 🔥 reverse match (INI KUNCI FIX LU)
            if p == pod and d == pol:
                return distance

        except:
            continue

    return 0

def load_distances():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_distances(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_all_ports():
    data = load_distances()
    ports = set()

    for route in data.keys():
        try:
            pol, pod = route.split(" - ")
            ports.add(pol.upper())
            ports.add(pod.upper())
        except:
            continue

    return sorted(list(ports))


# ==========================================================
# ⚙️ Page Config (WAJIB paling atas!)
# ==========================================================
st.set_page_config(
    page_title="Freight Calculator Barge",
    page_icon="https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/icon-512x512.png",
    layout="wide"
)

st.markdown("""
<style>

/* Base font */
html, body, [class*="css"]  {
    font-size: 13px !important;
}

/* Label */
label {
    font-size: 12px !important;
}

/* Input text & number */
input, select {
    font-size: 13px !important;
}

/* Button */
button {
    font-size: 13px !important;
    padding: 6px 10px !important;
}

/* Metric / big text */
h1, h2, h3 {
    font-size: 16px !important;
}

/* Caption kecil */
.small-text {
    font-size: 11px !important;
    color: #666;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* 🔥 BUTTON CALCULATE UTAMA */
div.stButton > button {
    background: linear-gradient(135deg, #6495ED, #FFFFFF, #6495ED);
    color: Black;
    font-weight: bold;
    border-radius: 12px;
    height: 48px;
    font-size: 14px;
    border: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.35);
}

/* 🔥 EFFECT HOVER */
div.stButton > button:hover {
    background: linear-gradient(135deg, #6495ED, #FFFFFF, #6495ED);
    color: Black;
    font-weight: bold;
    border-radius: 12px;
    height: 48px;
    font-size: 14px;
    border: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.35);
}

/* 🔥 BIAR ADA JARAK DI HP */
div.stButton {
    margin-top: 10px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* ===== FIX RESULT BOX DARK MODE ===== */

div[data-testid="stAlert"] {
    color: white !important;
}

/* SUCCESS */
div[data-testid="stAlert"][kind="success"] {
    background-color: #1b5e20 !important;
    border-left: 5px solid #00e676 !important;
}

/* WARNING */
div[data-testid="stAlert"][kind="warning"] {
    background-color: #ff8f00 !important;
    border-left: 5px solid #ffd54f !important;
}

/* ERROR */
div[data-testid="stAlert"][kind="error"] {
    background-color: #b71c1c !important;
    border-left: 5px solid #ff5252 !important;
}

/* FORCE TEXT ALWAYS VISIBLE */
html, body, [class*="css"] {
    color: #f5f5f5 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* ===== LOGIN BUTTON (BIRU) ===== */
div.stButton > button[kind="primary"] {
    background: #2563eb !important;
    color: white !important;
    border-radius: 10px !important;
    height: 42px !important;
    font-weight: 600 !important;
    border: none !important;
}

/* hover login */
div.stButton > button[kind="primary"]:hover {
    background: #1d4ed8 !important;
}

/* ===== CREATE ACCOUNT (KOTAK POLOS) ===== */
div.stButton > button[kind="secondary"] {
    background: transparent !important;   /* ❌ tidak ada warna */
    color: #2563eb !important;
    border: 1px solid #cbd5e1 !important; /* kotak tetap ada */
    border-radius: 10px !important;
    height: 42px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}

/* hover tetap soft */
div.stButton > button[kind="secondary"]:hover {
    background: #f8fafc !important;
    border-color: #2563eb !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* ===== CONTAINER ===== */
div[role="radiogroup"] {
    display: flex;
    gap: 8px;
    width: 100%;
}

/* ===== DEFAULT OPTION ===== */
div[role="radiogroup"] label {
    flex: 1;
    text-align: center;
    padding: 8px 10px;
    border-radius: 10px;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 12px;
    color: #334155;
}

/* hide radio dot */
div[role="radiogroup"] input {
    display: none;
}

/* 🔥 ACTIVE (SELECTED) */
div[role="radiogroup"] label:has(input:checked) {
    background: #2563eb !important;
    color: white !important;
    font-weight: 600;
    box-shadow: 0 4px 10px rgba(37,99,235,0.35);
    transform: scale(1.05);
    border: none;
}

/* hover */
div[role="radiogroup"] label:hover {
    background: #e2e8f0;
}

</style>
""", unsafe_allow_html=True)


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


# ====== FIREBASE AUTH ======
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]
AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
REGISTER_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

def login_user(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def register_user(email, password):
    res = requests.post(REGISTER_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()


# ✅ AUTO LOGIN DARI COOKIE (WAJIB DI ATAS)
if cookies.get("logged_in") == "true":
    st.session_state.logged_in = True
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

# ===== POPUP INFO =====
if "show_info" not in st.session_state:
    st.session_state.show_info = False

# ==========================================================
# 🚀 INTRO / ONBOARDING SCREEN (FINAL VERSION)
# ==========================================================
if not st.session_state.hide_intro:

    # 🔥 Biar posisi lebih tengah (mobile friendly)
    st.markdown("""
    <style>
    .block-container {
        padding-top: 5vh;
        padding-bottom: 5vh;
    }
    </style>
    """, unsafe_allow_html=True)

    # ===== UI INTRO =====
    st.markdown("""
    <div style="
        text-align:center;
        padding:50px 25px;
    ">

    <h1 style="
        font-size:28px;
        font-weight:800;
        margin-bottom:5px;
    ">
        🚢 Freight Calculator
    </h1>

    <p style="
        font-size:13px;
        color:#64748B;
        margin-bottom:20px;
    ">
        Cost, Freight & Profit Analysis Tool
    </p>

    <div style="
        display:grid;
        grid-template-columns: repeat(2, 1fr);
        gap:12px;
        margin-top:10px;
        font-size:12px;
    ">

    <div style="
        background:linear-gradient(135deg,#e0f2fe,#f8fafc);
        padding:12px;
        border-radius:12px;
        font-weight:500;
    ">
        ⚡ Cepat
    </div>

    <div style="
        background:linear-gradient(135deg,#e0f2fe,#f8fafc);
        padding:12px;
        border-radius:12px;
        font-weight:500;
    ">
        🎯 Akurat
    </div>

    <div style="
        background:linear-gradient(135deg,#e0f2fe,#f8fafc);
        padding:12px;
        border-radius:12px;
        font-weight:500;
    ">
        💰 Hitung untung/rugi
    </div>

    <div style="
        background:linear-gradient(135deg,#e0f2fe,#f8fafc);
        padding:12px;
        border-radius:12px;
        font-weight:500;
    ">
        🤝🏻 Nego lebih percaya diri
    </div>

    </div>

    <div style="
        margin-top:30px;
        font-size:11px;
        color:#94a3b8;
    ">
        Built with ❤️ by <b style="color:#2563eb;">Muhammad Iqna</b>
    </div>

    </div>
    """, unsafe_allow_html=True)

    # ===== CHECKBOX =====
    dont_show = st.checkbox("Jangan tampilkan lagi")

    # ===== BUTTON =====
    if st.button("🚀 Get Started", use_container_width=True):

        if dont_show:
            cookies["hide_intro"] = "true"
            cookies.save()

        st.session_state.hide_intro = True
        st.session_state.page = "login"
        st.rerun()

    st.stop()

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
                st.error("Email atau password salah")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Create New Account", type="secondary", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

        st.stop()


    # =========================
    # PAGE: REGISTER
    # =========================
    if st.session_state.page == "register":

        st.markdown("<h2 style='text-align:center;'>Create Account</h2>", unsafe_allow_html=True)

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

# ==========================================================
# ⚙️ PRESET PARAMETER KAPAL (non-intrusive)
# - ditaruh di expander sidebar yang default tertutup
# - tidak mengubah layout main / posisi expander lain
# ==========================================================
preset_params = {
    "270 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 85, "price_fuel": 25000,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 40000000,
        "docking": 40000000, "maintenance": 40000000,
        "certificate": 40000000, "premi_nm": 50000, "other_cost": 10000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 4, "port_stay_pod": 4
    },
    "300 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 115, "price_fuel": 25000,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 50000000,
        "docking": 50000000, "maintenance": 50000000,
        "certificate": 45000000, "premi_nm": 50000, "other_cost": 15000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 5, "port_stay_pod": 5
    },
    "330 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 130, "price_fuel": 25000,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 60000000,
        "docking": 60000000, "maintenance": 60000000,
        "certificate": 50000000, "premi_nm": 50000, "other_cost": 20000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 5, "port_stay_pod": 5
    },
    "Custom": {
        "speed_laden": 0, "speed_ballast": 0,
        "consumption": 0, "price_fuel": 0,
        "consumption_fw": 0, "price_fw": 0,
        "charter": 0, "crew": 0, "insurance": 0,
        "docking": 000, "maintenance": 0,
        "certificate": 0, "premi_nm": 0, "other_cost": 0,
        "port_cost_pol": 0, "port_cost_pod": 0, "asist_tug": 0,
        "port_stay_pol": 0, "port_stay_pod": 0
    }
}


cargo_qty_default = {
    "270 ft": {
        "Coal (MT)": 5500,
        "Nickel (MT)": 5500,
        "Bauxite (MT)": 5500,
        "Sand (M3)": 3500,
        "Split (M3)": 3500
    },
    "300 ft": {
        "Coal (MT)": 7500,
        "Nickel (MT)": 7500,
        "Bauxite (MT)": 7500,
        "Sand (M3)": 4700,
        "Split (M3)": 5000
    },
    "330 ft": {
        "Coal (MT)": 11500,
        "Nickel (MT)": 11500,
        "Bauxite (MT)": 11500,
        "Sand (M3)": 6000,
        "Split (M3)": 6500
    }
}

def get_default_cargo(barge, cargo_type):
    return float(cargo_qty_default.get(barge, {}).get(cargo_type, 0))

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
    consumption = st.number_input("Fuel Consumption (L/hr)", value=st.session_state.get("consumption", 0))
    price_fuel = st.number_input("Fuel Price (Rp/L)", value=st.session_state.get("price_fuel", 0))

    consumption_fw = st.number_input("FW Consumption (Ton/Day)", value=st.session_state.get("consumption_fw", 0))
    price_fw = st.number_input("FW Price (Rp/Ton)", value=st.session_state.get("price_fw", 0))

if mode == "Owner":
    with st.sidebar.expander("🏗️ Cost (Owner)", expanded=False):
        charter = st.number_input("Angsuran (Rp/Month)", value=st.session_state.get("charter", 0))
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

# ===== LOGOUT =====
st.sidebar.markdown("### Account")
st.sidebar.write(f"**{st.session_state.email}**")
if st.sidebar.button("**Log Out**"):
    st.session_state.logged_in = False

    cookies["logged_in"] = "false"
    cookies["email"] = ""
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
                ### 📘 Cara Pakai

                1. Pilih Barge Class
                2. Pilih POL & POD
                3. Isi cargo & freight
                4. Klik CALCULATE
                """)

    # ❌ kalau modal tidak ada → pakai fallback
    else:

        st.markdown("## ℹ️ Info & Tutorial")

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
            
            💡 Tips:
            Gunakan data real supaya hasil lebih akurat
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
        ["Bauxite (MT)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)"],
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
    unit = type_cargo.split()[1]

    qyt_cargo = st.number_input(
        f"Qty ({unit})",
        value=st.session_state.qyt_cargo,
        key="qyt_cargo",
        label_visibility="collapsed"
    )

st.markdown("### 💸 Freight Pricing")

freight_price_input = st.number_input("Freight Rate (Rp/MT)", 0)


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
        pol_pod_day = pol_pod_hour / 24
        pod_pol_day = pod_pol_hour / 24
            
        # Waktu sailing (hour) based on speed inputs (hours)
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        # total voyage in days (sailing hours converted to days + port stays)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_voyage_days_round = int(total_voyage_days) if total_voyage_days % 1 < 0.5 else int(total_voyage_days) + 1

        # consumptions
        total_consumption_fuel = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * total_voyage_days_round
        cost_fw = total_consumption_fw * price_fw
        cost_fuel = total_consumption_fuel * price_fuel

        # core costs
        charter_cost = (charter / 30) * total_voyage_days
        crew_cost = (crew / 30) * total_voyage_days if mode == "Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode == "Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode == "Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode == "Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode == "Owner" else 0
        total_general_overhead = ((opex_office + depreciation_kapal) / 30) * total_voyage_days
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
            charter_cost, crew_cost, insurance_cost, docking_cost, maintenance_cost, certificate_cost,total_general_overhead, 
            premi_cost, port_cost, cost_fuel, cost_fw, other_cost, additional_total
        ])

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # ===== REVENUE CALC =====
        revenue_user = freight_price_input * qyt_cargo
        pph_user = revenue_user * 0.012
        profit_user = revenue_user - total_cost - pph_user
        profit_percent_user = (profit_user / total_cost * 100) if total_cost > 0 else 0

        # ===== TCE CALCULATION =====
        tce_base_cost = cost_fuel + cost_fw + port_cost + premi_cost

        tce_per_day = (
            tce_base_cost / total_voyage_days
            if total_voyage_days > 0 else 0
        )

        tce_per_month = tce_per_day * 30

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
        <h4 style="color:#93c5fd;">🚢 Voyage Summary</h4>

        • Cargo Type: <b>{type_cargo}</b><br>
        • Route: <b>{port_pol} → {port_pod}</b><br>
        • Distance POL → POD: <b>{distance_pol_pod:,.0f} NM</b><br>
        • Total Cargo: <b>{qyt_cargo:,.0f} {type_cargo.split()[1]}</b><br>
        • Total Voyage: <b>{total_voyage_days:.1f} Days</b>
        <span style="font-size:11px; color:#bbb;">
        (sailing POL→POD {pol_pod_day:.1f} Days - POD→POL {pod_pol_day:.1f} Days)
        </span><br>
        • Freight Cost: <b style="color:#0f172a;">Rp {freight_cost_mt:,.0f}</b>

        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg, #f8fafc, #eef5ff);
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            color:#0f172a;;
            border-left:5px solid #ff9800;
            box-shadow:0 4px 12px rgba(0,0,0,0.4);
        ">
        <h4 style="color:#ff9800;">⛽ Fuel & Water</h4>

        • Fuel Consumption: <b>{total_consumption_fuel:,.0f} Ltr</b><br>
        • Fuel Cost: <b>Rp {cost_fuel:,.0f}</b><br>
        
        • Freshwater Consumption: <b>{total_consumption_fw:,.0f} Ton</b><br>
        • FW Cost: <b>Rp {cost_fw:,.0f}</b>

        </div>
        """, unsafe_allow_html=True)

        
        st.subheader("🏗️ Cost Summary")

        # =========================
        # 1. BREAKDOWN COST ONLY
        # =========================
        for k, v in owner_data.items():
            st.write(f"• {k}: Rp {v:,.0f}")

        # =========================
        # 2. ADDITIONAL COST (sekali saja)
        # =========================
        if additional_breakdown:
            st.markdown("➕ Additional Costs")
            for k, v in additional_breakdown.items():
                st.write(f"• {k}: Rp {v:,.0f}")

        # =========================
        # 3. GENERAL OVERHEAD (sekali saja)
        # =========================
        st.write(f"• General Overhead: Rp {total_general_overhead:,.0f}")

        # =========================
        # 4. SUMMARY (WAJIB SINGLE OUTPUT)
        # =========================
        st.success(f"💰 Total Cost: Rp {total_cost:,.0f}")
        st.warning(f"📦 Freight Cost: Rp {freight_cost_mt:,.0f} / {type_cargo.split()[1]}")


        # ===== FREIGHT PRICE CALCULATION USER (Conditional) =====
        if freight_price_input > 0:
            st.markdown(f"""
            <div style="
                background:#e8f5e9;
                padding:12px;
                border-radius:12px;
                margin-bottom:10px;
            ">
            <h4>💰 Profit</h4>
            • Revenue: <b>Rp {revenue_user:,.0f}</b><br>
            • Profit: <b>Rp {profit_user:,.0f}</b><br>
            • Margin: <b>{profit_percent_user:.2f}%</b>
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

        # ===== PDF GENERATOR =====
        def create_pdf(username):
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=25,
                leftMargin=25,
                topMargin=0,
                bottomMargin=0
            )

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='HeaderBlue', fontSize=16, textColor=colors.HexColor("#0d47a1"), alignment=1, spaceAfter=4))
            styles.add(ParagraphStyle(name='SubHeader', fontSize=12, textColor=colors.HexColor("#0d47a1"), spaceAfter=4, fontName='Helvetica-Bold'))
            styles.add(ParagraphStyle(name='NormalSmall', fontSize=8, leading=12))
            styles.add(ParagraphStyle(name='Bold', fontSize=11, fontName='Helvetica-Bold'))

            elements = []
            def fmt_rp(x):
                return f"Rp {x:,.0f}"

            def pct_of_total(x):
                try:
                    if total_cost and total_cost > 0:
                        return f"   ({(x / total_cost) * 100:.1f}%)"
                    else:
                        return " (0.0%)"
                except Exception:
                    return " (0.0%)"

            # ===== HEADER =====
            title = Paragraph("<b>Freight Calculation Report</b>", styles['HeaderBlue'])
            elements.append(title)
            elements.append(Spacer(1, 2))

            # ===== VOYAGE INFO =====
            elements.append(Paragraph("Voyage Information", styles['SubHeader']))
            voyage_data = [
                ["Port Of Loading", port_pol],
                ["Port Of Discharge", port_pod],
                ["Next Port", next_port],
                ["Cargo Quantity", f"{qyt_cargo:,.0f} {type_cargo.split()[1]}"],
                ["Distance (NM)", f"{distance_pol_pod:,.0f}"],
                ["Total Voyage (Days)", f"{total_voyage_days:.2f}"],
            ]
            t_voyage = Table(voyage_data, colWidths=[9*cm, 9*cm])
            t_voyage.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements += [t_voyage, Spacer(1, 4)]

            # ===== OPERATIONAL COST =====
            elements.append(Paragraph("Operational & Cost Summary", styles['SubHeader']))
            calc_data = [
                ["Total Sailing Time (Hour)", f"{sailing_time:.2f}"],
                ["Total Consumption Fuel (Ltr)", f"{total_consumption_fuel:,.0f}"],
                ["Total Consumption Freshwater (Ton)", f"{total_consumption_fw:,.0f}"],
                ["Fuel Cost (Rp)", f"{fmt_rp(cost_fuel)}{pct_of_total(cost_fuel)}"],
                ["Freshwater Cost (Rp)", f"{fmt_rp(cost_fw)}{pct_of_total(cost_fw)}"],
                ["Total General Overhead (Voyage)", fmt_rp(total_general_overhead) + pct_of_total(total_general_overhead)],
            ]

            for k, v in owner_data.items():
                calc_data.append([k, f"{fmt_rp(v)}{pct_of_total(v)}"])

            if additional_breakdown:
                calc_data.append(["--- Additional Costs ---", ""])
                for k, v in additional_breakdown.items():
                    calc_data.append([k, f"{fmt_rp(v)}{pct_of_total(v)}"])

            calc_data.append(["Total Cost (Rp)", f"Rp {total_cost:,.0f}"])
            calc_data.append([f"Freight Cost ({type_cargo.split()[1]})", f"Rp {freight_cost_mt:,.0f}"])

            t_calc = Table(calc_data, colWidths=[9*cm, 9*cm])
            t_calc.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements += [t_calc, Spacer(1, 4)]

            # ===== FREIGHT PRICE =====
            if freight_price_input > 0:
                elements.append(Paragraph("Freight Price Calculation User", styles['SubHeader']))
                fpc_data = [
                    ["Freight Price (Rp/MT)", f"Rp {freight_price_input:,.0f}"],
                    ["Revenue", f"Rp {revenue_user:,.0f}"],
                    ["PPH 1.2%", f"Rp {pph_user:,.0f}"],
                    ["Profit", f"Rp {profit_user:,.0f}"],
                    ["Profit %", f"{profit_percent_user:.2f} %"],
                ]
                t_fpc = Table(fpc_data, colWidths=[9*cm, 9*cm])
                t_fpc.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                ]))
                elements += [t_fpc, Spacer(1, 4)]

            # ===== TCE =====
            elements.append(Paragraph("Time Charter Equivalent (TCE)", styles['SubHeader']))

            tce_data = [
                ["Base Cost (Fuel + FW + Port + Premi)", fmt_rp(tce_base_cost)],
                ["TCE Per Day", f"{fmt_rp(tce_per_day)} / Day"],
                ["TCE Per Month", f"{fmt_rp(tce_per_month)} / Month"],
            ]

            t_tce = Table(tce_data, colWidths=[9*cm, 9*cm])
            t_tce.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))

            elements += [t_tce, Spacer(1, 4)]


            # ===== PROFIT SCENARIO =====
            elements.append(Paragraph("Profit Scenario 0–75%", styles['SubHeader']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t_profit = Table(profit_table, colWidths=[3*cm, 3.8*cm, 3.8*cm, 3.8*cm, 3.8*cm])
            t_profit.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements += [t_profit, Spacer(1, 4)]

            # ===== FOOTER =====
            footer_text = f"Generated by {username} | https://freight-calculator-mobile.streamlit.app"
            elements.append(Paragraph(footer_text, styles['NormalSmall']))

            # Tanggal generated di bawah footer
            generated_date = Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", styles['NormalSmall'])
            elements.append(generated_date)

            # ===== BUILD PDF =====
            doc.build(elements)
            buffer.seek(0)
            return buffer

        # ===== GENERATE PDF & DOWNLOAD BUTTON =====
        pdf_buffer = create_pdf(username=st.session_state.email)
        selected_barge = st.session_state.get("preset_selected", "Custom")
        file_name = f"Freight Report {selected_barge} {port_pol}-{port_pod} ({datetime.now():%d%m%Y}).pdf"

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")

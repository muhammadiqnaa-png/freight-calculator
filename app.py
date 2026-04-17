import streamlit as st
import math
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

# ✅ TAMBAH DI SINI
def clean_data(data):
    clean = []
    for d in data:
        if isinstance(d, dict) and "pol" in d and "pod" in d:
            clean.append(d)
    return clean

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

def get_next_ports(pod):
    data = load_distances()
    pod = (pod or "").upper()

    next_ports = []

    for route in data.keys():
        try:
            pol, dest = route.split(" - ")
            if pol.upper() == pod:
                next_ports.append(dest.upper())
        except:
            continue

    return sorted(list(set(next_ports)))


# ==========================================================
# ⚙️ Page Config (WAJIB paling atas!)
# ==========================================================
st.set_page_config(
    page_title="Freight Calculator Barge",
    page_icon="https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/icon-512x512.png",
    layout="centered"
)

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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ✅ AUTO LOGIN DARI COOKIE (WAJIB DI ATAS)
if cookies.get("logged_in") == "true":
    st.session_state.logged_in = True
    st.session_state.email = cookies.get("email")

# ===== LOGIN =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align:center; padding:10px;">
        <h3>🚢 Freight Calculator Login</h3>
    </div>
    """, unsafe_allow_html=True)
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login 🚀"):
            ok, data = login_user(email, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.email = email

                cookies["logged_in"] = "true"
                cookies["email"] = email
                cookies.save()

                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Email or password incorrect!")

    with tab_register:
        email = st.text_input("Email Register")
        password = st.text_input("Password Register", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(email, password)
            if ok:
                st.success("Registration successful! Please login.")
            else:
                st.error("Failed to register. Email may already exist.")
    st.stop()
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

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

# ==== PRESET SEGMEN ====

# Default state
if "preset_selected" not in st.session_state:
    st.session_state.preset_selected = "Custom"

# Handler untuk update state
def update_preset():
    st.session_state.preset_selected = st.session_state.preset_control


def get_pods_by_pol(pol):
    data = load_distances()
    pol = (pol or "").upper()

    pods = set()

    for route in data.keys():
        try:
            p, d = route.split(" - ")
            if p.upper() == pol:
                pods.add(d.upper())
        except:
            continue

    return sorted(list(pods))


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

preset = st.sidebar.segmented_control(
    "Size Barge",
    ["270 ft", "300 ft", "330 ft", "Custom"],
    key="preset_control"
)

selected = st.session_state.preset_control

if selected in preset_params:
    for k, v in preset_params[selected].items():
        st.session_state[k] = v


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

    raw_data = load_distances()

    clean = []

    # 🔥 HANDLE 2 FORMAT (lama + baru)
    if isinstance(raw_data, dict):
        # format lama: "POL - POD": distance
        for route, dist in raw_data.items():
            try:
                pol, pod = route.split(" - ")
                clean.append({
                    "POL": pol,
                    "POD": pod,
                    "Distance (NM)": dist
                })
            except:
                continue

    elif isinstance(raw_data, list):
        # format baru: list of dict
        for d in raw_data:
            if isinstance(d, dict):
                clean.append({
                    "POL": d.get("pol", "-"),
                    "POD": d.get("pod", "-"),
                    "Distance (NM)": d.get("distance", 0)
                })

    # ===== TAMPILKAN =====
    if not clean:
        st.info("Belum ada data distance")
    else:
        df = pd.DataFrame(clean)
        st.dataframe(df, use_container_width=True, hide_index=True)
            

# ===== SIDEBAR PARAMETERS =====
with st.sidebar.expander("⚙️ Operational Input", expanded=False):
    speed_laden = st.number_input("Speed Laden (knot)", value=st.session_state.get("speed_laden", 0.0))
    speed_ballast = st.number_input("Speed Ballast (knot)", value=st.session_state.get("speed_ballast", 0.0))

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
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False

    cookies["logged_in"] = "false"
    cookies["email"] = ""
    cookies.save()

    st.success("Successfully logged out.")
    st.rerun()

# ===== MAIN INPUT =====
st.title("")
st.markdown("""
<div style="
    text-align:center;
    padding:10px;
    border-radius:12px;
    background:#0d47a1;
    color:white;
    margin-bottom:15px;
">
    <h3 style="margin:0;">🚢 Freight Calculator</h3>
    <p style="margin:0; font-size:12px;">Mobile Shipping Cost & Profit Tool</p>
</div>
""", unsafe_allow_html=True)


# ===== MAIN INPUT =====
st.title("🚢 Freight Calculator Barge")

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

st.markdown("### 📦 Cargo Information")

col1, col2 = st.columns(2)
with col1:
    type_cargo = st.selectbox(
    "Cargo Type",
    ["Bauxite (MT)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)"],
    key="cargo_type"
    )

with col2:
    selected_barge = st.session_state.get("preset_selected", "Custom")
    selected_cargo = st.session_state.get("cargo_type", None)

    # default value logic
    default_qty = 0

    if selected_barge in cargo_qty_default:
        if selected_cargo in cargo_qty_default[selected_barge]:
            default_qty = cargo_qty_default[selected_barge][selected_cargo]

    qyt_cargo = st.number_input(
        "Cargo Quantity",
        value=float(default_qty),
        step=1.0
    )

    st.caption(f"Suggested capacity for {selected_barge} - {selected_cargo}")


st.markdown("### 💸 Freight Pricing")

freight_price_input = st.number_input("Freight Rate (Rp/MT)", 0)


st.markdown("")

calculate = st.button(
    "🚀 CALCULATE NOW",
    use_container_width=True
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
            background:#f5f7ff;
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
        ">
        <h4>🚢 Voyage Summary</h4>
        
        • Cargo Type: <b>{type_cargo}</b><br>
        • Route: <b>{port_pol} → {port_pod}</b><br>
        • Distance POL → POD: <b>{distance_pol_pod:,.0f} NM</b><br>
        • Total Cargo: <b>{qyt_cargo:,.0f} {type_cargo.split()[1]}</b><br>
        • Total Voyage: <b>{total_voyage_days:.2f} Days</b><br>
        <span style="margin-left:10px; font-size:12px; color:#666;">
        (sailing time POL→POD {pol_pod_day:.2f} Days - POD→POL {pod_pol_day:.2f} Days )
        </span><br>
        • Freight Cost: <b>Rp {freight_cost_mt:,.0f} / {type_cargo.split()[1]}</b>

        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background:#fff3e0;
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
        ">
        <h4>⛽ Fuel & Water</h4>
        • Fuel Consumption: <b>{total_consumption_fuel:,.0f} Ltr</b><br>
        • Fuel Cost: <b>Rp {cost_fuel:,.0f}</b><br>
        <br>
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
            background:#e3f2fd;
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
        ">
        <h4>⏱️ TCE</h4>
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
            footer_text = f"Generated by {username} | https://freight-calculator-barge-byiqna.streamlit.app/"
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
        file_name = f"Freight Report {selected_barge} {port_pol}-{port_pod} ({datetime.now():%Y%m%d}).pdf"

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")

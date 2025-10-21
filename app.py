import streamlit as st
import math
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import requests

st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# ===== CONFIG FIREBASE =====
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]
FIREBASE_DB_URL = st.secrets.get("FIREBASE_DB_URL", "https://freight-calculator-2b823-default-rtdb.asia-southeast1.firebasedatabase.app")

AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
REGISTER_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

def login_user(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def register_user(email, password):
    res = requests.post(REGISTER_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def _safe_key(k: str):
    if k is None:
        return ""
    return str(k).replace(".", "_").replace("@", "_").replace(" ", "_")

def save_parameters_to_fb(email, id_token, preset_name, payload: dict):
    safe_email = _safe_key(email)
    safe_name = _safe_key(preset_name)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters/{safe_name}.json?auth={id_token}"
    res = requests.put(url, json=payload, timeout=10)
    return res.ok, res.text

def list_presets_from_fb(email, id_token):
    safe_email = _safe_key(email)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters.json?auth={id_token}"
    res = requests.get(url, timeout=10)
    if res.ok:
        return res.json() or {}, None
    return None, res.text

def load_preset_from_fb(email, id_token, preset_name):
    safe_email = _safe_key(email)
    safe_name = _safe_key(preset_name)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters/{safe_name}.json?auth={id_token}"
    res = requests.get(url, timeout=10)
    if res.ok:
        return res.json() or {}, None
    return None, res.text

# ===== AUTH =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>🔐 Login Freight Calculator</h2>", unsafe_allow_html=True)
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login 🚀"):
            ok, data = login_user(email, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.idToken = data.get("idToken")
                st.session_state.localId = data.get("localId")
                st.success("Login successful!")
                st.rerun()
            else:
                err = data.get("error", {}).get("message", "") if isinstance(data, dict) else data
                st.error(f"Login gagal: {err}")

    with tab_register:
        r_email = st.text_input("Email Register")
        r_password = st.text_input("Password Register", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(r_email, r_password)
            if ok:
                st.success("Registrasi berhasil — silakan login.")
            else:
                err = data.get("error", {}).get("message", "") if isinstance(data, dict) else data
                st.error(f"Gagal register: {err}")
    st.stop()

# ===== SIDEBAR ACCOUNT / LOGOUT =====
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.get('email','-')}**")
if st.sidebar.button("🚪 Log Out"):
    keys_to_clear = [k for k in list(st.session_state.keys()) if k not in ("_sidebar","_rerun_count")]
    for k in keys_to_clear:
        st.session_state.pop(k, None)
    st.session_state.logged_in = False
    st.experimental_rerun()

# ===== MODE =====
mode = st.sidebar.selectbox("Mode", ["Owner", "Charter"])

# ===== SIDEBAR PARAMETERS =====
COMMON_KEYS = [
    "speed_laden", "speed_ballast",
    "consumption", "price_fuel",
    "consumption_fw", "price_fw",
    "port_cost_pol", "port_cost_pod", "asist_tug",
    "port_stay_pol", "port_stay_pod",
    "other_cost"
]
OWNER_KEYS = [
    "charter", "crew", "insurance", "docking", "maintenance", "certificate", "premi_nm"
]
CHARTER_KEYS = [
    "charter", "premi_nm"
]

for k in COMMON_KEYS + OWNER_KEYS + CHARTER_KEYS:
    if k not in st.session_state:
        st.session_state[k] = 0

# ===== SIDEBAR INPUT WIDGETS =====
with st.sidebar.expander("🚢 Speed"):
    st.number_input("Speed Laden (knot)", 0.0, key="speed_laden")
    st.number_input("Speed Ballast (knot)", 0.0, key="speed_ballast")
with st.sidebar.expander("⛽ Fuel"):
    st.number_input("Consumption Fuel (liter/hour)", 0, key="consumption")
    st.number_input("Price Fuel (Rp/Ltr)", 0, key="price_fuel")
with st.sidebar.expander("💧 Freshwater"):
    st.number_input("Consumption Freshwater (Ton/Day)", 0, key="consumption_fw")
    st.number_input("Price Freshwater (Rp/Ton)", 0, key="price_fw")
if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        st.number_input("Angsuran (Rp/Month)", 0, key="charter")
        st.number_input("Crew (Rp/Month)", 0, key="crew")
        st.number_input("Insurance (Rp/Month)", 0, key="insurance")
        st.number_input("Docking (Rp/Month)", 0, key="docking")
        st.number_input("Maintenance (Rp/Month)", 0, key="maintenance")
        st.number_input("Certificate (Rp/Month)", 0, key="certificate")
        st.number_input("Premi (Rp/NM)", 0, key="premi_nm")
        st.number_input("Other Cost (Rp)", 0, key="other_cost")
else:
    with st.sidebar.expander("🏗️ Charter Cost"):
        st.number_input("Charter Hire (Rp/Month)", 0, key="charter")
        st.number_input("Premi (Rp/NM)", 0, key="premi_nm")
        st.number_input("Other Cost (Rp)", 0, key="other_cost")
with st.sidebar.expander("⚓ Port Cost"):
    st.number_input("Port Cost POL (Rp)", 0, key="port_cost_pol")
    st.number_input("Port Cost POD (Rp)", 0, key="port_cost_pod")
    st.number_input("Asist Tug (Rp)", 0, key="asist_tug")
with st.sidebar.expander("🕓 Port Stay"):
    st.number_input("POL (Days)", 0, key="port_stay_pol")
    st.number_input("POD (Days)", 0, key="port_stay_pod")

# ===== SAVE / LOAD PRESETS =====
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Presets (save per user & per mode)")
preset_name = st.sidebar.text_input("Preset name", key="preset_name")

def keys_for_mode(m):
    if m == "Owner":
        return COMMON_KEYS + OWNER_KEYS
    else:
        return COMMON_KEYS + CHARTER_KEYS

if st.sidebar.button("💾 Save Parameter"):
    if not preset_name:
        st.sidebar.error("Masukkan nama preset terlebih dahulu.")
    else:
        idt = st.session_state.get("idToken")
        email = st.session_state.get("email")
        if not idt or not email:
            st.sidebar.error("Auth token hilang. Silakan logout dan login lagi.")
        else:
            keys = keys_for_mode(mode)
            payload = {k: st.session_state.get(k, 0) for k in keys}
            payload["mode"] = mode
            payload["saved_at"] = datetime.utcnow().isoformat()
            ok, msg = save_parameters_to_fb(email, idt, preset_name, payload)
            if ok:
                st.sidebar.success(f"Preset '{preset_name}' tersimpan.")
            else:
                st.sidebar.error(f"Gagal simpan preset: {msg}")

if st.sidebar.button("🔄 Reset Parameter:"):
    for k in COMMON_KEYS + list(set(OWNER_KEYS + CHARTER_KEYS)):
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

# ===== LOAD PRESETS =====
presets = {}
idt = st.session_state.get("idToken")
email = st.session_state.get("email")
if idt and email:
    presets_dict, err = list_presets_from_fb(email, idt)
    if presets_dict is None:
        st.sidebar.warning("Tidak bisa mengambil preset (cek DB/rule).")
    else:
        presets = presets_dict

preset_list = ["-- Select preset --"] + sorted(list(presets.keys()))
sel_preset = st.sidebar.selectbox("Saved presets", preset_list, key="sel_preset")

if st.sidebar.button("🔄 Refresh / Load Selected"):
    if sel_preset == "-- Select preset --":
        st.sidebar.error("Pilih preset terlebih dahulu atau pilih -- Select preset -- untuk kosongkan.")
    else:
        if not (idt and email):
            st.sidebar.error("Auth token hilang. Silakan logout dan login ulang.")
        else:
            data_json, err = load_preset_from_fb(email, idt, sel_preset)
            if data_json is None:
                st.sidebar.error(f"Gagal load preset: {err}")
            else:
                preset_mode = data_json.get("mode", None)
                allowed_keys = set(COMMON_KEYS + OWNER_KEYS + CHARTER_KEYS)
                for k, v in data_json.items():
                    if k not in allowed_keys or not isinstance(k, str):
                        continue
                    try:
                        if k in OWNER_KEYS:
                            if preset_mode == "Owner":
                                st.session_state[k] = v
                        elif k in CHARTER_KEYS:
                            if preset_mode == "Charter":
                                st.session_state[k] = v
                        else:
                            st.session_state[k] = v
                    except Exception as e:
                        st.warning(f"Gagal set session_state[{k}]: {e}")
                st.sidebar.success(f"Preset '{sel_preset}' dimuat ke sidebar.")
                st.experimental_rerun()

# ===== MAIN INPUT =====
st.title("🚢 Freight Calculator Barge")
col1, col2, col3 = st.columns(3)
with col1:
    port_pol = st.text_input("Port Of Loading", key="port_pol")
with col2:
    port_pod = st.text_input("Port Of Discharge", key="port_pod")
with col3:
    next_port = st.text_input("Next Port", key="next_port")
type_cargo = st.selectbox("Type Cargo", ["Bauxite (M3)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)"], key="type_cargo")
qyt_cargo = st.number_input("Cargo Quantity", 0.0, key="qyt_cargo")
distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0, key="distance_pol_pod")
distance_pod_pol = st.number_input("Distance POD - POL (NM)", 0.0, key="distance_pod_pol")
freight_price_input = st.number_input("Freight Price (Rp/MT) (optional)", 0, key="freight_price_input")

# ===== CALCULATION & PDF GENERATOR =====
if st.button("Calculate Freight 💸"):
    try:
        # --- Calculation ---
        s_laden = st.session_state.get("speed_laden") or 1
        s_ballast = st.session_state.get("speed_ballast") or 1
        sailing_time = (distance_pol_pod / s_laden) + (distance_pod_pol / s_ballast)
        total_voyage_days = (sailing_time / 24) + (st.session_state.get("port_stay_pol", 0) + st.session_state.get("port_stay_pod", 0))
        total_voyage_days_round = int(total_voyage_days) if total_voyage_days % 1 < 0.5 else int(total_voyage_days) + 1

        total_consumption_fuel = (sailing_time * st.session_state.get("consumption", 0)) + ((st.session_state.get("port_stay_pol", 0) + st.session_state.get("port_stay_pod", 0)) * 120)
        total_consumption_fw = st.session_state.get("consumption_fw", 0) * total_voyage_days_round
        cost_fw = total_consumption_fw * st.session_state.get("price_fw", 0)
        cost_fuel = total_consumption_fuel * st.session_state.get("price_fuel", 0)
        port_cost = st.session_state.get("port_cost_pol", 0) + st.session_state.get("port_cost_pod", 0) + st.session_state.get("asist_tug", 0)
        other_cost = st.session_state.get("other_cost", 0)

        if mode == "Owner":
            fixed_cost = (st.session_state.get("charter", 0) + st.session_state.get("crew", 0) +
                          st.session_state.get("insurance", 0) + st.session_state.get("docking", 0) +
                          st.session_state.get("maintenance", 0) + st.session_state.get("certificate", 0))
            premi_nm = st.session_state.get("premi_nm", 0)
        else:
            fixed_cost = st.session_state.get("charter", 0)
            premi_nm = st.session_state.get("premi_nm", 0)

        total_cost = cost_fw + cost_fuel + port_cost + fixed_cost + other_cost
        total_nm = distance_pol_pod + distance_pod_pol
        suggested_freight = total_cost / qyt_cargo if qyt_cargo else 0
        profit = (freight_price_input - suggested_freight) * qyt_cargo if freight_price_input else 0

        st.subheader("📊 Summary")
        st.write(f"Total Voyage Days: {total_voyage_days_round} Days")
        st.write(f"Total Fuel Cost: Rp {cost_fuel:,.0f}")
        st.write(f"Total Freshwater Cost: Rp {cost_fw:,.0f}")
        st.write(f"Port & Tug Cost: Rp {port_cost:,.0f}")
        st.write(f"Fixed Cost: Rp {fixed_cost:,.0f}")
        st.write(f"Other Cost: Rp {other_cost:,.0f}")
        st.write(f"Total Cost: Rp {total_cost:,.0f}")
        st.write(f"Suggested Freight: Rp {suggested_freight:,.0f} / MT")
        st.write(f"Profit (if Freight Price Rp {freight_price_input:,.0f}): Rp {profit:,.0f}")

        # --- PDF Generator ---
        def generate_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elems = []

            elems.append(Paragraph("🚢 Freight Calculation Report", styles['Title']))
            elems.append(Spacer(1, 12))
            elems.append(Paragraph(f"Port of Loading: {port_pol}", styles['Normal']))
            elems.append(Paragraph(f"Port of Discharge: {port_pod}", styles['Normal']))
            elems.append(Paragraph(f"Next Port: {next_port}", styles['Normal']))
            elems.append(Paragraph(f"Cargo: {type_cargo}, Quantity: {qyt_cargo}", styles['Normal']))
            elems.append(Paragraph(f"Total Voyage Days: {total_voyage_days_round}", styles['Normal']))
            elems.append(Spacer(1, 12))

            data_table = [
                ["Description", "Cost (Rp)"],
                ["Fuel", f"{cost_fuel:,.0f}"],
                ["Freshwater", f"{cost_fw:,.0f}"],
                ["Port & Tug", f"{port_cost:,.0f}"],
                ["Fixed Cost", f"{fixed_cost:,.0f}"],
                ["Other Cost", f"{other_cost:,.0f}"],
                ["Total Cost", f"{total_cost:,.0f}"],
                ["Suggested Freight", f"{suggested_freight:,.0f} / MT"],
                ["Profit", f"{profit:,.0f}"]
            ]

            table = Table(data_table, hAlign='LEFT', colWidths=[250,150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black)
            ]))
            elems.append(table)
            doc.build(elems)
            buffer.seek(0)
            return buffer

        pdf_buffer = generate_pdf()
        st.download_button("📄 Download PDF Report", data=pdf_buffer, file_name=f"freight_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Error in calculation: {e}")

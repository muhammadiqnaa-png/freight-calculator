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

# ====== FIREBASE CONFIG & AUTH ======
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]
FIREBASE_DB_URL = st.secrets.get("FIREBASE_DB_URL", "")

AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
REGISTER_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

def login_user(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def register_user(email, password):
    res = requests.post(REGISTER_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def _safe_key(email_or_name: str):
    if email_or_name is None:
        return ""
    return str(email_or_name).replace(".", "_").replace("@", "_").replace(" ", "_")

def save_parameters_to_fb(email, id_token, preset_name, data: dict):
    if not FIREBASE_DB_URL:
        return False, "FIREBASE_DB_URL not configured in secrets."
    safe_email = _safe_key(email)
    safe_name = _safe_key(preset_name)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters/{safe_name}.json?auth={id_token}"
    res = requests.put(url, json=data)
    return res.ok, res.text

def list_presets_from_fb(email, id_token):
    if not FIREBASE_DB_URL:
        return None, "FIREBASE_DB_URL not configured in secrets."
    safe_email = _safe_key(email)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters.json?auth={id_token}"
    res = requests.get(url)
    if res.ok:
        return res.json() or {}, None
    return None, res.text

def load_preset_from_fb(email, id_token, preset_name):
    if not FIREBASE_DB_URL:
        return None, "FIREBASE_DB_URL not configured in secrets."
    safe_email = _safe_key(email)
    safe_name = _safe_key(preset_name)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters/{safe_name}.json?auth={id_token}"
    res = requests.get(url)
    if res.ok:
        return res.json() or {}, None
    return None, res.text

def delete_preset_from_fb(email, id_token, preset_name):
    if not FIREBASE_DB_URL:
        return False, "FIREBASE_DB_URL not configured in secrets."
    safe_email = _safe_key(email)
    safe_name = _safe_key(preset_name)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters/{safe_name}.json?auth={id_token}"
    res = requests.delete(url)
    return res.ok, res.text

# ===== LOGIN =====
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
                st.error(f"Email or password incorrect! {err}")

    with tab_register:
        r_email = st.text_input("Email Register")
        r_password = st.text_input("Password Register", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(r_email, r_password)
            if ok:
                st.success("Registration successful! Please login.")
            else:
                err = data.get("error", {}).get("message", "") if isinstance(data, dict) else data
                st.error(f"Failed to register. {err}")
    st.stop()

# ===== LOGOUT =====
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.get('email','-')}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.session_state.pop("idToken", None)
    st.session_state.pop("localId", None)
    st.success("Successfully logged out.")
    st.rerun()

# ===== MODE =====
mode = st.sidebar.selectbox("Mode", ["Owner", "Charter"])

# ===== REFRESH ALL BUTTON =====
if st.sidebar.button("🔄 Refresh All"):
    for key in st.session_state.keys():
        if key not in ["logged_in", "email", "idToken", "localId", "sel_preset"]:
            st.session_state[key] = 0 if isinstance(st.session_state[key], (int, float)) else ""
    st.rerun()

# ===== SIDEBAR PARAMETERS =====
charter = crew = insurance = docking = maintenance = certificate = premi_nm = other_cost = 0

with st.sidebar.expander("🚢 Speed"):
    speed_laden = st.number_input("Speed Laden (knot)", 0.0, key="speed_laden")
    speed_ballast = st.number_input("Speed Ballast (knot)", 0.0, key="speed_ballast")

with st.sidebar.expander("⛽ Fuel"):
    consumption = st.number_input("Consumption Fuel (liter/hour)", 0, key="consumption")
    price_fuel = st.number_input("Price Fuel (Rp/Ltr)", 0, key="price_fuel")

with st.sidebar.expander("💧 Freshwater"):
    consumption_fw = st.number_input("Consumption Freshwater (Ton/Day)", 0, key="consumption_fw")
    price_fw = st.number_input("Price Freshwater (Rp/Ton)", 0, key="price_fw")

if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        charter = st.number_input("Angsuran (Rp/Month)", 0, key="charter")
        crew = st.number_input("Crew (Rp/Month)", 0, key="crew")
        insurance = st.number_input("Insurance (Rp/Month)", 0, key="insurance")
        docking = st.number_input("Docking (Rp/Month)", 0, key="docking")
        maintenance = st.number_input("Maintenance (Rp/Month)", 0, key="maintenance")
        certificate = st.number_input("Certificate (Rp/Month)", 0, key="certificate")
        premi_nm = st.number_input("Premi (Rp/NM)", 0, key="premi_nm")
        other_cost = st.number_input("Other Cost (Rp)", 0, key="other_cost")
else:
    with st.sidebar.expander("🏗️ Charter Cost"):
        charter = st.number_input("Charter Hire (Rp/Month)", 0, key="charter")
        premi_nm = st.number_input("Premi (Rp/NM)", 0, key="premi_nm")
        other_cost = st.number_input("Other Cost (Rp)", 0, key="other_cost")

with st.sidebar.expander("⚓ Port Cost"):
    port_cost_pol = st.number_input("Port Cost POL (Rp)", 0, key="port_cost_pol")
    port_cost_pod = st.number_input("Port Cost POD (Rp)", 0, key="port_cost_pod")
    asist_tug = st.number_input("Asist Tug (Rp)", 0, key="asist_tug")

with st.sidebar.expander("🕓 Port Stay"):
    port_stay_pol = st.number_input("POL (Days)", 0, key="port_stay_pol")
    port_stay_pod = st.number_input("POD (Days)", 0, key="port_stay_pod")

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

# --- Save / Load UI ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Presets (save / load your parameters)")
preset_name = st.sidebar.text_input("Preset name", key="preset_name")
if st.sidebar.button("💾 Save Parameter"):
    input_keys = ["speed_laden", "speed_ballast", "consumption", "price_fuel",
                  "consumption_fw", "price_fw", "charter", "crew", "insurance",
                  "docking", "maintenance", "certificate", "premi_nm", "other_cost",
                  "port_cost_pol", "port_cost_pod", "asist_tug",
                  "port_stay_pol", "port_stay_pod",
                  "port_pol", "port_pod", "next_port",
                  "type_cargo", "qyt_cargo", "distance_pol_pod", "distance_pod_pol",
                  "freight_price_input", "mode"]
    payload = {k: st.session_state.get(k, 0) for k in input_keys}
    payload["saved_at"] = datetime.utcnow().isoformat()

    if not preset_name:
        st.sidebar.error("Please provide a preset name before saving.")
    else:
        idt = st.session_state.get("idToken")
        email = st.session_state.get("email")
        ok, msg = save_parameters_to_fb(email, idt, preset_name, payload)
        if ok:
            st.sidebar.success(f"Preset '{preset_name}' saved.")
        else:
            st.sidebar.error(f"Failed to save preset: {msg}")

presets = {}
idt = st.session_state.get("idToken")
email = st.session_state.get("email")
if FIREBASE_DB_URL and idt and email:
    presets_dict, err = list_presets_from_fb(email, idt)
    if presets_dict is None:
        st.sidebar.warning("Could not fetch presets.")
    else:
        presets = presets_dict

preset_list = ["-- Select preset --"] + sorted(list(presets.keys()))
sel_preset = st.sidebar.selectbox("Saved presets", preset_list, key="sel_preset")

colL, colR = st.sidebar.columns([1,1])
with colL:
    if st.button("📂 Load Parameter"):
        if sel_preset == "-- Select preset --":
            st.sidebar.error("Select a preset first.")
        else:
            data_json, err = load_preset_from_fb(email, idt, sel_preset)
            if data_json is None:
                st.sidebar.error(f"Failed to load preset: {err}")
            else:
                for k, v in data_json.items():
                    if k in st.session_state:
                        st.session_state[k] = v
                st.rerun()

with colR:
    if st.button("🗑️ Delete Parameter"):
        if sel_preset == "-- Select preset --":
            st.sidebar.error("Select a preset to delete.")
        else:
            ok, msg = delete_preset_from_fb(email, idt, sel_preset)
            if ok:
                st.sidebar.success(f"Preset '{sel_preset}' deleted.")
                st.rerun()
            else:
                st.sidebar.error(f"Failed to delete preset: {msg}")

# ===== CALCULATION =====
def calc_total_fuel(consumption, speed, distance, price):
    hours = distance / speed if speed else 0
    total_liter = consumption * hours
    return total_liter * price

laden_cost = calc_total_fuel(consumption, speed_laden, distance_pol_pod, price_fuel)
ballast_cost = calc_total_fuel(consumption, speed_ballast, distance_pod_pol, price_fuel)
fuel_cost_total = laden_cost + ballast_cost

water_cost_total = (consumption_fw * (port_stay_pol + port_stay_pod)) * price_fw

port_total = port_cost_pol + port_cost_pod + asist_tug
owner_cost_total = charter + crew + insurance + docking + maintenance + certificate + other_cost
premi_total = premi_nm * (distance_pol_pod + distance_pod_pol)

total_cost = fuel_cost_total + water_cost_total + port_total + owner_cost_total + premi_total
freight_price = freight_price_input if freight_price_input > 0 else total_cost / (qyt_cargo if qyt_cargo else 1)
profit = freight_price * qyt_cargo - total_cost

st.markdown("### 💰 Calculation Summary")
st.write(f"**Fuel Cost:** Rp {fuel_cost_total:,.0f}")
st.write(f"**Freshwater Cost:** Rp {water_cost_total:,.0f}")
st.write(f"**Port & Tug Cost:** Rp {port_total:,.0f}")
st.write(f"**Owner/Charter Cost:** Rp {owner_cost_total:,.0f}")
st.write(f"**Premi Cost:** Rp {premi_total:,.0f}")
st.write(f"**Total Cost:** Rp {total_cost:,.0f}")
st.write(f"**Freight Price Used:** Rp {freight_price:,.0f}")
st.write(f"**Profit:** Rp {profit:,.0f}")

# ===== PDF EXPORT =====
def export_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Freight Calculation Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    data_table = [
        ["Item", "Value (Rp)"],
        ["Fuel Cost", f"{fuel_cost_total:,.0f}"],
        ["Freshwater Cost", f"{water_cost_total:,.0f}"],
        ["Port & Tug Cost", f"{port_total:,.0f}"],
        ["Owner/Charter Cost", f"{owner_cost_total:,.0f}"],
        ["Premi Cost", f"{premi_total:,.0f}"],
        ["Total Cost", f"{total_cost:,.0f}"],
        ["Freight Price", f"{freight_price:,.0f}"],
        ["Profit", f"{profit:,.0f}"]
    ]

    table = Table(data_table, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button("📄 Export PDF"):
    pdf_buffer = export_pdf()
    st.download_button("Download PDF", pdf_buffer, file_name="freight_report.pdf", mime="application/pdf")

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import requests

st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# =================== Firebase Config ===================
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]
FIREBASE_DB_URL = st.secrets.get(
    "FIREBASE_DB_URL",
    "https://freight-calculator-2b823-default-rtdb.asia-southeast1.firebasedatabase.app"
)
AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
REGISTER_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

def login_user(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def register_user(email, password):
    res = requests.post(REGISTER_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def _safe_key(k: str):
    if k is None: return ""
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
    if res.ok: return res.json() or {}, None
    return None, res.text

def load_preset_from_fb(email, id_token, preset_name):
    safe_email = _safe_key(email)
    safe_name = _safe_key(preset_name)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters/{safe_name}.json?auth={id_token}"
    res = requests.get(url, timeout=10)
    if res.ok: return res.json() or {}, None
    return None, res.text

# =================== Auth ===================
if "logged_in" not in st.session_state: st.session_state.logged_in = False

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
                st.success("Login berhasil!")
                st.experimental_rerun()
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

# =================== Sidebar Account / Logout ===================
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.get('email','-')}**")
if st.sidebar.button("🚪 Log Out"):
    keys_to_clear = [k for k in list(st.session_state.keys()) if k not in ("_sidebar","_rerun_count")]
    for k in keys_to_clear: st.session_state.pop(k, None)
    st.session_state.logged_in = False
    st.experimental_rerun()

# =================== Mode ===================
mode = st.sidebar.selectbox("Mode", ["Owner", "Charter"])

# =================== Keys ===================
COMMON_KEYS = ["speed_laden","speed_ballast","consumption","price_fuel","consumption_fw","price_fw",
               "port_cost_pol","port_cost_pod","asist_tug","port_stay_pol","port_stay_pod","other_cost"]
OWNER_KEYS = ["charter","crew","insurance","docking","maintenance","certificate","premi_nm"]
CHARTER_KEYS = ["charter","premi_nm"]

# =================== Helper Load Preset ===================
def load_preset_safe(data_json):
    allowed_keys = set(COMMON_KEYS + OWNER_KEYS + CHARTER_KEYS)
    st.session_state["preset_mode"] = data_json.get("mode", None)
    for k, v in data_json.items():
        if k in allowed_keys:
            st.session_state[f"preset_{k}"] = v

# =================== Sidebar Widgets ===================
# Speed
with st.sidebar.expander("🚢 Speed"):
    st.number_input("Speed Laden (knot)", value=st.session_state.get("preset_speed_laden", 0.0), key="speed_laden")
    st.number_input("Speed Ballast (knot)", value=st.session_state.get("preset_speed_ballast", 0.0), key="speed_ballast")

# Fuel
with st.sidebar.expander("⛽ Fuel"):
    st.number_input("Consumption Fuel (liter/hour)", value=st.session_state.get("preset_consumption", 0), key="consumption")
    st.number_input("Price Fuel (Rp/Ltr)", value=st.session_state.get("preset_price_fuel", 0), key="price_fuel")

# Freshwater
with st.sidebar.expander("💧 Freshwater"):
    st.number_input("Consumption Freshwater (Ton/Day)", value=st.session_state.get("preset_consumption_fw", 0), key="consumption_fw")
    st.number_input("Price Freshwater (Rp/Ton)", value=st.session_state.get("preset_price_fw", 0), key="price_fw")

# Owner / Charter
if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        for k in OWNER_KEYS + ["other_cost"]:
            st.number_input(f"{k.replace('_',' ').title()} (Rp)", value=st.session_state.get(f"preset_{k}", 0), key=k)
else:
    with st.sidebar.expander("🏗️ Charter Cost"):
        for k in CHARTER_KEYS + ["other_cost"]:
            st.number_input(f"{k.replace('_',' ').title()} (Rp)", value=st.session_state.get(f"preset_{k}", 0), key=k)

# Port Cost
with st.sidebar.expander("⚓ Port Cost"):
    st.number_input("Port Cost POL (Rp)", value=st.session_state.get("preset_port_cost_pol",0), key="port_cost_pol")
    st.number_input("Port Cost POD (Rp)", value=st.session_state.get("preset_port_cost_pod",0), key="port_cost_pod")
    st.number_input("Asist Tug (Rp)", value=st.session_state.get("preset_asist_tug",0), key="asist_tug")

# Port Stay
with st.sidebar.expander("🕓 Port Stay"):
    st.number_input("POL (Days)", value=st.session_state.get("preset_port_stay_pol",0), key="port_stay_pol")
    st.number_input("POD (Days)", value=st.session_state.get("preset_port_stay_pod",0), key="port_stay_pod")

# =================== Preset Save/Load ===================
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Presets")

preset_name = st.sidebar.text_input("Preset name", key="preset_name")
idt = st.session_state.get("idToken")
email = st.session_state.get("email")

# List presets
presets = {}
if idt and email:
    presets_dict, err = list_presets_from_fb(email, idt)
    if presets_dict: presets = presets_dict

preset_list = ["-- Select preset --"] + sorted(list(presets.keys()))
sel_preset = st.sidebar.selectbox("Saved presets", preset_list, key="sel_preset")

# Save
if st.sidebar.button("💾 Save Parameter"):
    if not preset_name: st.sidebar.error("Masukkan nama preset.")
    else:
        keys = COMMON_KEYS + (OWNER_KEYS if mode=="Owner" else CHARTER_KEYS)
        payload = {k: st.session_state.get(k,0) for k in keys}
        payload["mode"] = mode
        payload["saved_at"] = datetime.utcnow().isoformat()
        ok,msg = save_parameters_to_fb(email,idt,preset_name,payload)
        if ok: st.sidebar.success(f"Preset '{preset_name}' tersimpan.")
        else: st.sidebar.error(f"Gagal simpan preset: {msg}")

# Load
if st.sidebar.button("🔄 Refresh / Load Selected"):
    if sel_preset=="-- Select preset --": st.sidebar.error("Pilih preset.")
    else:
        data_json, err = load_preset_from_fb(email,idt,sel_preset)
        if data_json is None: st.sidebar.error(f"Gagal load: {err}")
        else:
            load_preset_safe(data_json)
            st.sidebar.success(f"Preset '{sel_preset}' dimuat.")
            st.rerun()

# =================== Main Input ===================
st.title("🚢 Freight Calculator Barge")
col1,col2,col3 = st.columns(3)
with col1: port_pol = st.text_input("Port Of Loading", key="port_pol")
with col2: port_pod = st.text_input("Port Of Discharge", key="port_pod")
with col3: next_port = st.text_input("Next Port", key="next_port")

type_cargo = st.selectbox("Type Cargo", ["Bauxite (M3)","Sand (M3)","Coal (MT)","Nickel (MT)","Split (M3)"], key="type_cargo")
qyt_cargo = st.number_input("Cargo Quantity", 0.0, key="qyt_cargo")
distance_pol_pod = st.number_input("Distance POL-POD (NM)", 0.0, key="distance_pol_pod")
distance_pod_pol = st.number_input("Distance POD-POL (NM)", 0.0, key="distance_pod_pol")
freight_price_input = st.number_input("Freight Price (Rp/MT) (optional)", 0, key="freight_price_input")

# =================== Calculation & PDF ===================
if st.button("Calculate Freight 💸"):
    try:
        s_laden = st.session_state.get("speed_laden") or 1
        s_ballast = st.session_state.get("speed_ballast") or 1
        sailing_time = (distance_pol_pod/s_laden)+(distance_pod_pol/s_ballast)
        total_voyage_days = (sailing_time/24)+(st.session_state.get("port_stay_pol",0)+st.session_state.get("port_stay_pod",0))
        total_voyage_days_round = int(total_voyage_days) if total_voyage_days%1<0.5 else int(total_voyage_days)+1

        cost_fuel = st.session_state.get("consumption",0)*sailing_time*st.session_state.get("price_fuel",0)
        cost_fw = st.session_state.get("consumption_fw",0)*total_voyage_days_round*st.session_state.get("price_fw",0)
        port_cost = st.session_state.get("port_cost_pol",0)+st.session_state.get("port_cost_pod",0)+st.session_state.get("asist_tug",0)
        other_cost = st.session_state.get("other_cost",0)

        if mode=="Owner":
            fixed_cost = (st.session_state.get("charter",0)+st.session_state.get("crew",0)+
                          st.session_state.get("insurance",0)+st.session_state.get("docking",0)+
                          st.session_state.get("maintenance",0)+st.session_state.get("certificate",0))
            premi_nm = st.session_state.get("premi_nm",0)
        else:
            fixed_cost = st.session_state.get("charter",0)
            premi_nm = st.session_state.get("premi_nm",0)

        total_cost = cost_fuel+cost_fw+port_cost+fixed_cost+other_cost
        suggested_freight = total_cost/qyt_cargo if qyt_cargo>0 else 0
        profit = (freight_price_input-suggested_freight)*qyt_cargo if freight_price_input>0 else 0

        st.subheader("📊 Summary")
        st.write(f"Total Voyage Days: {total_voyage_days_round} Days")
        st.write(f"Total Cost: Rp {total_cost:,.0f}")
        st.write(f"Suggested Freight: Rp {suggested_freight:,.0f}/MT")
        if freight_price_input>0:
            st.write(f"Profit if Freight={freight_price_input}: Rp {profit:,.0f}")

        # PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer,pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [Paragraph("Freight Calculator Report", styles['Title']), Spacer(1,12)]
        elements.append(Paragraph(f"Port POL: {port_pol}", styles['Normal']))
        elements.append(Paragraph(f"Port POD: {port_pod}", styles['Normal']))
        elements.append(Paragraph(f"Cargo Quantity: {qyt_cargo}", styles['Normal']))
        t = Table([
            ["Item","Value"],
            ["Total Voyage Days", f"{total_voyage_days_round}"],
            ["Total Cost","Rp {:,.0f}".format(total_cost)],
            ["Suggested Freight","Rp {:,.0f}".format(suggested_freight)],
            ["Profit","Rp {:,.0f}".format(profit)]
        ], colWidths=[200,200])
        t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        st.download_button("📥 Download PDF", data=buffer, file_name=f"Freight_{datetime.now():%Y%m%d}.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Error: {e}")


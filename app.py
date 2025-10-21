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

# ====== AUTH FUNCTIONS ======
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

# ===== REFRESH ALL =====
if st.sidebar.button("🔄 Refresh All"):
    keys_to_clear = [
        "speed_laden","speed_ballast","consumption","price_fuel",
        "consumption_fw","price_fw","charter","crew","insurance",
        "docking","maintenance","certificate","premi_nm","other_cost",
        "port_cost_pol","port_cost_pod","asist_tug",
        "port_stay_pol","port_stay_pod",
        "port_pol","port_pod","next_port",
        "type_cargo","qyt_cargo","distance_pol_pod","distance_pod_pol",
        "freight_price_input","preset_name","sel_preset"
    ]
    for k in keys_to_clear:
        if k in st.session_state:
            if k in ["port_pol","port_pod","next_port","type_cargo","preset_name","sel_preset"]:
                st.session_state[k] = ""
            else:
                st.session_state[k] = 0
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

col1,col2,col3 = st.columns(3)
with col1: port_pol = st.text_input("Port Of Loading", key="port_pol")
with col2: port_pod = st.text_input("Port Of Discharge", key="port_pod")
with col3: next_port = st.text_input("Next Port", key="next_port")

type_cargo = st.selectbox("Type Cargo", ["Bauxite (M3)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)"], key="type_cargo")
qyt_cargo = st.number_input("Cargo Quantity", 0.0, key="qyt_cargo")
distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0, key="distance_pol_pod")
distance_pod_pol = st.number_input("Distance POD - POL (NM)", 0.0, key="distance_pod_pol")
freight_price_input = st.number_input("Freight Price (Rp/MT) (optional)", 0, key="freight_price_input")

# --- Preset Save / Load / Delete ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Presets (save / load your parameters)")
preset_name = st.sidebar.text_input("Preset name", key="preset_name")

# Save preset
if st.sidebar.button("💾 Save Parameter"):
    payload = {k: st.session_state.get(k, 0) for k in [
        "mode","speed_laden","speed_ballast","consumption","price_fuel",
        "consumption_fw","price_fw","charter","crew","insurance","docking",
        "maintenance","certificate","premi_nm","other_cost","port_cost_pol",
        "port_cost_pod","asist_tug","port_stay_pol","port_stay_pod",
        "port_pol","port_pod","next_port","type_cargo","qyt_cargo",
        "distance_pol_pod","distance_pod_pol","freight_price_input"
    ]}
    payload["saved_at"] = datetime.utcnow().isoformat()
    if not preset_name:
        st.sidebar.error("Please provide a preset name before saving.")
    else:
        idt = st.session_state.get("idToken")
        email = st.session_state.get("email")
        ok,msg = save_parameters_to_fb(email,idt,preset_name,payload)
        if ok: st.sidebar.success(f"Preset '{preset_name}' saved.")
        else: st.sidebar.error(f"Failed to save preset: {msg}")

# List presets
presets = {}
idt = st.session_state.get("idToken")
email = st.session_state.get("email")
if idt and email:
    presets_dict, err = list_presets_from_fb(email, idt)
    if presets_dict: presets = presets_dict

preset_list = ["-- Select preset --"] + sorted(list(presets.keys()))
sel_preset = st.sidebar.selectbox("Saved presets", preset_list, key="sel_preset")

colL, colR = st.sidebar.columns([1,1])
with colL:
    if st.button("📂 Load Parameter"):
        if sel_preset != "-- Select preset --":
            data_json, err = load_preset_from_fb(email,idt,sel_preset)
            if data_json:
                for k,v in data_json.items():
                    if k in st.session_state: st.session_state[k]=v
                st.rerun()
            else: st.sidebar.error(f"Failed to load preset: {err}")
        else: st.sidebar.error("Select a preset first.")

with colR:
    if st.button("🗑️ Delete Parameter"):
        if sel_preset != "-- Select preset --":
            ok,msg = delete_preset_from_fb(email,idt,sel_preset)
            if ok:
                st.sidebar.success(f"Preset '{sel_preset}' deleted.")
                st.rerun()
            else: st.sidebar.error(f"Failed to delete preset: {msg}")
        else: st.sidebar.error("Select a preset to delete.")

# ===== PERHITUNGAN =====
def calc_total_fuel(consumption, speed, distance):
    return consumption*(distance/speed) if speed else 0

if st.button("Calculate Freight 💸"):
    try:
        sailing_time = (distance_pol_pod/speed_laden if speed_laden else 0) + (distance_pod_pol/speed_ballast if speed_ballast else 0)
        total_voyage_days = sailing_time/24 + port_stay_pol + port_stay_pod
        total_voyage_days_round = int(total_voyage_days) if total_voyage_days % 1 < 0.5 else int(total_voyage_days)+1

        total_consumption_fuel = (calc_total_fuel(consumption,speed_laden,distance_pol_pod) +
                                  calc_total_fuel(consumption,speed_ballast,distance_pod_pol))
        cost_fuel = total_consumption_fuel*price_fuel

        total_consumption_fw = consumption_fw*total_voyage_days_round
        cost_fw = total_consumption_fw*price_fw

        charter_cost = (charter/30)*total_voyage_days
        crew_cost = (crew/30)*total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance/30)*total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking/30)*total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance/30)*total_voyage_days if mode=="Owner" else 0
        certificate_cost = (certificate/30)*total_voyage_days if mode=="Owner" else 0
        premi_cost = premi_nm*distance_pol_pod
        port_cost = port_cost_pol+port_cost_pod+asist_tug

        total_cost = sum([charter_cost,crew_cost,insurance_cost,docking_cost,
                          maintenance_cost,certificate_cost,premi_cost,port_cost,
                          cost_fuel,cost_fw,other_cost])

        freight_cost_mt = total_cost/qyt_cargo if qyt_cargo>0 else 0
        revenue_user = freight_price_input*qyt_cargo
        pph_user = revenue_user*0.012
        profit_user = revenue_user-total_cost-pph_user
        profit_percent_user = (profit_user/revenue_user*100) if revenue_user>0 else 0

        # Display results
        st.subheader("📋 Calculation Results")
        st.markdown(f"""
**Total Voyage (Days):** {total_voyage_days:.2f}  
**Total Consumption Fuel (Ltr):** {total_consumption_fuel:,.0f}  
**Total Consumption Freshwater (Ton):** {total_consumption_fw:,.0f}  
**Fuel Cost:** Rp {cost_fuel:,.0f}  
**Freshwater Cost:** Rp {cost_fw:,.0f}  
**Total Cost:** Rp {total_cost:,.0f}  
**Freight Cost/MT:** Rp {freight_cost_mt:,.0f}
""")
        if freight_price_input>0:
            st.subheader("💰 Freight Price User Calculation")
            st.markdown(f"""
**Freight Price (Rp/MT):** Rp {freight_price_input:,.0f}  
**Revenue:** Rp {revenue_user:,.0f}  
**PPH 1.2%:** Rp {pph_user:,.0f}  
**Profit:** Rp {profit_user:,.0f}  
**Profit %:** {profit_percent_user:.2f}%
""")

        # Profit Scenario Table
        data=[]
        for p in range(0,55,5):
            freight_persen = freight_cost_mt*(1+p/100)
            revenue = freight_persen*qyt_cargo
            pph = revenue*0.012
            profit = revenue-total_cost-pph
            data.append([f"{p}%",f"Rp {freight_persen:,.0f}",f"Rp {revenue:,.0f}",f"Rp {pph:,.0f}",f"Rp {profit:,.0f}"])
        df_profit=pd.DataFrame(data,columns=["Profit %","Freight (Rp)","Revenue (Rp)","PPH 1.2% (Rp)","Profit (Rp)"])
        st.subheader("💹 Profit Scenario 0–50%")
        st.dataframe(df_profit,use_container_width=True)

        # PDF Export
        def export_pdf():
            buffer=BytesIO()
            doc=SimpleDocTemplate(buffer,pagesize=A4)
            styles=getSampleStyleSheet()
            elements=[Paragraph("Freight Calculation Report",styles["Title"]),Spacer(1,12)]
            table_data=[df_profit.columns.to_list()]+df_profit.values.tolist()
            t=Table(table_data,colWidths=[60,110,110,110,110])
            t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),1,colors.black)]))
            elements.append(t)
            doc.build(elements)
            buffer.seek(0)
            return buffer

        if st.button("📄 Export PDF"):
            pdf_buffer=export_pdf()
            st.download_button("Download PDF",pdf_buffer,file_name="freight_report.pdf",mime="application/pdf")

    except Exception as e:
        st.error(f"Error: {e}")


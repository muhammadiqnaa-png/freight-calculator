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

# =================== Sidebar Widgets ===================
def number_input_safe(label, key, preset_key=None, min_value=0, float_mode=False):
    val = st.session_state.get(preset_key, 0) if preset_key else st.session_state.get(key, 0)
    if float_mode:
        return st.number_input(label, value=float(val), key=key)
    else:
        return st.number_input(label, value=int(val), key=key)

with st.sidebar.expander("🚢 Speed"):
    number_input_safe("Speed Laden (knot)", "speed_laden", "preset_speed_laden", float_mode=True)
    number_input_safe("Speed Ballast (knot)", "speed_ballast", "preset_speed_ballast", float_mode=True)

with st.sidebar.expander("⛽ Fuel"):
    number_input_safe("Consumption Fuel (liter/hour)","consumption","preset_consumption")
    number_input_safe("Price Fuel (Rp/Ltr)","price_fuel","preset_price_fuel")

with st.sidebar.expander("💧 Freshwater"):
    number_input_safe("Consumption Freshwater (Ton/Day)","consumption_fw","preset_consumption_fw")
    number_input_safe("Price Freshwater (Rp/Ton)","price_fw","preset_price_fw")

if mode=="Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        for k in OWNER_KEYS+["other_cost"]:
            number_input_safe(k.replace("_"," ").title(), k, f"preset_{k}")
else:
    with st.sidebar.expander("🏗️ Charter Cost"):
        for k in CHARTER_KEYS+["other_cost"]:
            number_input_safe(k.replace("_"," ").title(), k, f"preset_{k}")

with st.sidebar.expander("⚓ Port Cost"):
    number_input_safe("Port Cost POL (Rp)","port_cost_pol","preset_port_cost_pol")
    number_input_safe("Port Cost POD (Rp)","port_cost_pod","preset_port_cost_pod")
    number_input_safe("Asist Tug (Rp)","asist_tug","preset_asist_tug")

with st.sidebar.expander("🕓 Port Stay"):
    number_input_safe("POL (Days)","port_stay_pol","preset_port_stay_pol")
    number_input_safe("POD (Days)","port_stay_pod","preset_port_stay_pod")

# =================== Preset ===================
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Presets")
preset_name = st.sidebar.text_input("Preset name", key="preset_name")
idt = st.session_state.get("idToken")
email = st.session_state.get("email")
presets = {}
if idt and email:
    presets_dict, err = list_presets_from_fb(email,idt)
    if presets_dict: presets = presets_dict
preset_list = ["-- Select preset --"] + sorted(list(presets.keys()))
sel_preset = st.sidebar.selectbox("Saved presets", preset_list, key="sel_preset")

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

if st.sidebar.button("🔄 Refresh / Load Selected"):
    if sel_preset=="-- Select preset --": st.sidebar.error("Pilih preset.")
    else:
        data_json, err = load_preset_from_fb(email,idt,sel_preset)
        if data_json is None: st.sidebar.error(f"Gagal load: {err}")
        else:
            preset_mode = data_json.get("mode","Owner")
            allowed_keys = set(COMMON_KEYS + OWNER_KEYS + CHARTER_KEYS)
            for k,v in data_json.items():
                if k in allowed_keys: st.session_state[f"preset_{k}"]=v
            st.experimental_rerun()

# =================== Main Input ===================
st.title("🚢 Freight Calculator Barge")
col1,col2,col3 = st.columns(3)
with col1: port_pol = st.text_input("Port Of Loading", key="port_pol")
with col2: port_pod = st.text_input("Port Of Discharge", key="port_pod")
with col3: next_port = st.text_input("Next Port", key="next_port")
type_cargo = st.selectbox("Type Cargo", ["Bauxite (M3)","Sand (M3)","Coal (MT)","Nickel (MT)","Split (M3)"], key="type_cargo")
qyt_cargo = st.number_input("Cargo Quantity",0.0,key="qyt_cargo")
distance_pol_pod = st.number_input("Distance POL - POD (NM)",0.0,key="distance_pol_pod")
distance_pod_pol = st.number_input("Distance POD - POL (NM)",0.0,key="distance_pod_pol")
freight_price_input = st.number_input("Freight Price (Rp/MT) (optional)",0,key="freight_price_input")

# =================== Calculate ===================
if st.button("Calculate Freight 💸"):
    try:
        # Ambil nilai sidebar via preset safe get
        s_laden = st.session_state.get("speed_laden",1) or 1
        s_ballast = st.session_state.get("speed_ballast",1) or 1
        consumption = st.session_state.get("consumption",0)
        price_fuel = st.session_state.get("price_fuel",0)
        consumption_fw = st.session_state.get("consumption_fw",0)
        price_fw = st.session_state.get("price_fw",0)
        port_cost_pol = st.session_state.get("port_cost_pol",0)
        port_cost_pod = st.session_state.get("port_cost_pod",0)
        asist_tug = st.session_state.get("asist_tug",0)
        port_stay_pol = st.session_state.get("port_stay_pol",0)
        port_stay_pod = st.session_state.get("port_stay_pod",0)
        other_cost = st.session_state.get("other_cost",0)
        charter = st.session_state.get("charter",0)
        premi_nm = st.session_state.get("premi_nm",0)
        crew = st.session_state.get("crew",0)
        insurance = st.session_state.get("insurance",0)
        docking = st.session_state.get("docking",0)
        maintenance = st.session_state.get("maintenance",0)
        certificate = st.session_state.get("certificate",0)

        sailing_time = (distance_pol_pod/s_laden)+(distance_pod_pol/s_ballast)
        total_voyage_days = sailing_time/24 + port_stay_pol + port_stay_pod
        total_voyage_days_round = int(total_voyage_days) if total_voyage_days%1<0.5 else int(total_voyage_days)+1

        total_consumption_fuel = (sailing_time*consumption)+((port_stay_pol+port_stay_pod)*120)
        total_consumption_fw = consumption_fw*total_voyage_days_round
        cost_fw = total_consumption_fw*price_fw
        cost_fuel = total_consumption_fuel*price_fuel

        if mode=="Owner":
            charter_cost=(charter/30)*total_voyage_days
            crew_cost=(crew/30)*total_voyage_days
            insurance_cost=(insurance/30)*total_voyage_days
            docking_cost=(docking/30)*total_voyage_days
            maintenance_cost=(maintenance/30)*total_voyage_days
            certificate_cost=(certificate/30)*total_voyage_days
        else:
            charter_cost=(charter/30)*total_voyage_days
            crew_cost=insurance_cost=docking_cost=maintenance_cost=certificate_cost=0

        premi_cost=distance_pol_pod*premi_nm
        port_cost=port_cost_pol+port_cost_pod+asist_tug

        total_cost=sum([charter_cost,crew_cost,insurance_cost,docking_cost,maintenance_cost,certificate_cost,
                        premi_cost,port_cost,cost_fuel,cost_fw,other_cost])
        freight_cost_mt=total_cost/qyt_cargo if qyt_cargo>0 else 0

        revenue_user=freight_price_input*qyt_cargo
        pph_user=revenue_user*0.012
        profit_user=revenue_user-total_cost-pph_user
        profit_percent_user=(profit_user/revenue_user*100) if revenue_user>0 else 0

        # =================== Display ===================
        st.subheader("📋 Calculation Results")
        st.markdown(f"""
**Type Cargo:** {type_cargo}  
**Cargo Quantity:** {qyt_cargo:,.0f} {type_cargo.split()[1]}  
**Distance (NM) POL-POD:** {distance_pol_pod:,.0f}  
**Distance (NM) POD-POL:** {distance_pod_pol:,.0f}  
**Total Voyage (Days):** {total_voyage_days:.2f}  
**Total Sailing Time (Hour):** {sailing_time:.2f}  
**Total Consumption Fuel (Ltr):** {total_consumption_fuel:,.0f}  
**Total Consumption Freshwater (Ton):** {total_consumption_fw:,.0f}  
**Fuel Cost (Rp):** Rp {cost_fuel:,.0f}  
**Freshwater Cost (Rp):** Rp {cost_fw:,.0f}
""")
        if mode=="Owner":
            st.markdown("### 🏗️ Owner Costs Summary")
            owner_data = {
                "Angsuran": charter_cost,
                "Crew": crew_cost,
                "Insurance": insurance_cost,
                "Docking": docking_cost,
                "Maintenance": maintenance_cost,
                "Certificate": certificate_cost,
                "Premi": premi_cost,
                "Port Costs": port_cost,
                "Other Costs": other_cost
            }
        else:
            st.markdown("### 🏗️ Charter Costs Summary")
            owner_data = {
                "Charter Hire": charter_cost,
                "Premi": premi_cost,
                "Port Costs": port_cost,
                "Other Costs": other_cost
            }
        for k,v in owner_data.items(): st.markdown(f"- {k}: Rp {v:,.0f}")
        st.markdown(f"**🧮 Total Cost:** Rp {total_cost:,.0f}")
        st.markdown(f"**🧮 Freight Cost ({type_cargo.split()[1]}):** Rp {freight_cost_mt:,.0f}")

        if freight_price_input>0:
            st.subheader("💰 Freight Price Calculation User")
            st.markdown(f"""
**Freight Price (Rp/MT):** Rp {freight_price_input:,.0f}  
**Revenue:** Rp {revenue_user:,.0f}  
**PPH 1.2%:** Rp {pph_user:,.0f}  
**Profit:** Rp {profit_user:,.0f}  
**Profit %:** {profit_percent_user:.2f} %
""")
        else:
            st.info("Isi Freight Price jika ingin melihat perhitungan profit user.")

        # Profit Scenario
        data=[]
        for p in range(0,55,5):
            freight_persen=freight_cost_mt*(1+p/100)
            revenue=freight_persen*qyt_cargo
            pph=revenue*0.012
            profit=revenue-total_cost-pph
            data.append([f"{p}%", f"Rp {freight_persen:,.0f}", f"Rp {revenue:,.0f}", f"Rp {pph:,.0f}", f"Rp {profit:,.0f}"])
        df_profit=pd.DataFrame(data, columns=["Profit %","Freight (Rp)","Revenue (Rp)","PPH 1.2% (Rp)","Profit (Rp)"])
        st.subheader("💹 Profit Scenario 0–50%")
        st.dataframe(df_profit,use_container_width=True)

        # =================== PDF ===================
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=10,leftMargin=10,topMargin=10,bottomMargin=10)
        styles=getSampleStyleSheet()
        elements=[Paragraph("<b>Freight Calculator Report</b>", styles['Title']), Spacer(1,6)]
        elements.append(Paragraph("<b>Voyage Information</b>", styles['Heading3']))
        voyage_data=[
            ["Port Of Loading", port_pol],
            ["Port Of Discharge", port_pod],
            ["Next Port", next_port],
            ["Cargo Quantity", f"{qyt_cargo:,.0f} {type_cargo.split()[1]}"],
            ["Distance POL-POD", f"{distance_pol_pod:,.0f}"],
            ["Distance POD-POL", f"{distance_pod_pol:,.0f}"],
            ["Total Voyage Days", f"{total_voyage_days:.2f}"]
        ]
        t_voyage=Table(voyage_data,hAlign='LEFT',colWidths=[160,320])
        t_voyage.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
        elements.append(t_voyage)
        elements.append(Spacer(1,6))

        elements.append(Paragraph("<b>Calculation Results</b>", styles['Heading3']))
        calc_data=[
            ["Total Sailing Time (Hour)", f"{sailing_time:.2f}"],
            ["Total Consumption Fuel (Ltr)", f"{total_consumption_fuel:,.0f} Ltr"],
            ["Total Consumption Freshwater (Ton)", f"{total_consumption_fw:,.0f} Ton"],
            ["Fuel Cost (Rp)", f"Rp {cost_fuel:,.0f}"],
            ["Freshwater Cost (Rp)", f"Rp {cost_fw:,.0f}"]
        ]
        for k,v in owner_data.items(): calc_data.append([k,f"Rp {v:,.0f}"])
        calc_data.append(["Total Cost (Rp)", f"Rp {total_cost:,.0f}"])
        calc_data.append([f"Freight Cost ({type_cargo.split()[1]})", f"Rp {freight_cost_mt:,.0f}"])
        t_calc=Table(calc_data,hAlign='LEFT',colWidths=[200,200])
        t_calc.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
        elements.append(t_calc)
        elements.append(Spacer(1,6))

        if freight_price_input>0:
            elements.append(Paragraph("<b>Freight Price Calculation User</b>", styles['Heading3']))
            fpc_data=[
                ["Freight Price (Rp/MT)", f"Rp {freight_price_input:,.0f}"],
                ["Revenue", f"Rp {revenue_user:,.0f}"],
                ["PPH 1.2%", f"Rp {pph_user:,.0f}"],
                ["Profit", f"Rp {profit_user:,.0f}"],
                ["Profit %", f"{profit_percent_user:.2f} %"]
            ]
            t_fpc=Table(fpc_data,hAlign='LEFT',colWidths=[200,200])
            t_fpc.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
            elements.append(t_fpc)
            elements.append(Spacer(1,6))

        elements.append(Paragraph("<b>Profit Scenario 0–50%</b>", styles['Heading3']))
        profit_table=[df_profit.columns.to_list()]+df_profit.values.tolist()
        t_profit=Table(profit_table,hAlign='LEFT',colWidths=[60,110,110,110,110])
        t_profit.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
        elements.append(t_profit)
        elements.append(Spacer(1,6))
        elements.append(Paragraph(f"<i>Generated by Freight Calculator App</i>", styles['Normal']))
        doc.build(elements)
        buffer.seek(0)
        safe_pol=(port_pol or "POL").replace(" ","_")
        safe_pod=(port_pod or "POD").replace(" ","_")
        file_name=f"Freight_Report_{safe_pol}_{safe_pod}_{datetime.now():%Y%m%d}.pdf"
        st.download_button(label="📥 Download PDF Report", data=buffer, file_name=file_name, mime="application/pdf")

    except Exception as e:
        st.error(f"Error: {e}")

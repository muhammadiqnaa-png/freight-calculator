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
# Jika ingin override di kode: set FIREBASE_DB_URL = "https://your-db.firebaseio.com"
FIREBASE_DB_URL = st.secrets.get("FIREBASE_DB_URL", "https://freight-calculator-2b823-default-rtdb.asia-southeast1.firebasedatabase.app")

AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
REGISTER_URL = f"https://identitytool.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

def login_user(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def register_user(email, password):
    res = requests.post(REGISTER_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

# ----- helpers for realtime DB (REST) -----
def _safe_key(email_or_name: str):
    if email_or_name is None:
        return ""
    return str(email_or_name).replace(".", "_").replace("@", "_").replace(" ", "_")

def save_parameters_to_fb(email, id_token, preset_name, data: dict):
    """Simpan ke /users/{safe_email}/parameters/{safe_name}.json"""
    if not FIREBASE_DB_URL:
        return False, "FIREBASE_DB_URL tidak dikonfigurasi."
    safe_email = _safe_key(email)
    safe_name = _safe_key(preset_name)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters/{safe_name}.json?auth={id_token}"
    res = requests.put(url, json=data)
    return res.ok, res.text

def list_presets_from_fb(email, id_token):
    if not FIREBASE_DB_URL:
        return None, "FIREBASE_DB_URL tidak dikonfigurasi."
    safe_email = _safe_key(email)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters.json?auth={id_token}"
    res = requests.get(url)
    if res.ok:
        return res.json() or {}, None
    return None, res.text

def load_preset_from_fb(email, id_token, preset_name):
    if not FIREBASE_DB_URL:
        return None, "FIREBASE_DB_URL tidak dikonfigurasi."
    safe_email = _safe_key(email)
    safe_name = _safe_key(preset_name)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters/{safe_name}.json?auth={id_token}"
    res = requests.get(url)
    if res.ok:
        return res.json() or {}, None
    return None, res.text

def delete_preset_from_fb(email, id_token, preset_name):
    if not FIREBASE_DB_URL:
        return False, "FIREBASE_DB_URL tidak dikonfigurasi."
    safe_email = _safe_key(email)
    safe_name = _safe_key(preset_name)
    url = f"{FIREBASE_DB_URL}/users/{safe_email}/parameters/{safe_name}.json?auth={id_token}"
    res = requests.delete(url)
    return res.ok, res.text

# ===== LOGIN =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# show login/register if not logged in
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
                st.error(f"Email atau password salah! {err}")

    with tab_register:
        r_email = st.text_input("Email Register")
        r_password = st.text_input("Password Register", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(r_email, r_password)
            if ok:
                st.success("Registrasi berhasil! Silakan login.")
            else:
                err = data.get("error", {}).get("message", "") if isinstance(data, dict) else data
                st.error(f"Gagal registrasi. {err}")
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

# ===== SIDEBAR PARAMETERS =====
# default inits untuk menghindari NameError jika mode lain dipilih
charter = 0
crew = 0
insurance = 0
docking = 0
maintenance = 0
certificate = 0
premi_nm = 0
other_cost = 0

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

# ---------------------------
# Save / Load Preset (sidebar)
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Presets (save / load your parameters)")

# define key groups
COMMON_KEYS = [
    "speed_laden","speed_ballast",
    "consumption","price_fuel",
    "consumption_fw","price_fw",
    "port_cost_pol","port_cost_pod","asist_tug",
    "port_stay_pol","port_stay_pod",
    "port_pol","port_pod","next_port"
]
OWNER_KEYS = ["charter","crew","insurance","docking","maintenance","certificate","premi_nm","other_cost"]
CHARTER_KEYS = ["charter","premi_nm","other_cost"]
MAIN_INPUT_KEYS = ["type_cargo","qyt_cargo","distance_pol_pod","distance_pod_pol","freight_price_input"]

def _defaults_for_keys(keys):
    """Return sensible default for given widget key (string -> default)"""
    defaults = {}
    for k in keys:
        if k in ["port_pol","port_pod","next_port","type_cargo"]:
            defaults[k] = ""
        elif k in ["qyt_cargo","distance_pol_pod","distance_pod_pol","speed_laden","speed_ballast","consumption","price_fuel","consumption_fw","price_fw","port_cost_pol","port_cost_pod","asist_tug","port_stay_pol","port_stay_pod","charter","crew","insurance","docking","maintenance","certificate","premi_nm","other_cost","freight_price_input"]:
            # numeric defaults
            defaults[k] = 0
        else:
            defaults[k] = 0
    return defaults

preset_name = st.sidebar.text_input("Preset name", key="preset_name")

# Save button: save common + mode-specific + main input
if st.sidebar.button("💾 Save Parameter"):
    if not preset_name:
        st.sidebar.error("Masukkan nama preset terlebih dahulu.")
    else:
        idt = st.session_state.get("idToken")
        email = st.session_state.get("email")
        if not idt or not email:
            st.sidebar.error("Auth token tidak ada. Silakan logout & login ulang.")
        else:
            # choose which mode-specific keys to save
            mode_keys = OWNER_KEYS if mode == "Owner" else CHARTER_KEYS
            keys_to_save = COMMON_KEYS + mode_keys + MAIN_INPUT_KEYS
            payload = {}
            for k in keys_to_save:
                payload[k] = st.session_state.get(k, _defaults_for_keys([k])[k])
            payload["mode"] = mode
            payload["saved_at"] = datetime.utcnow().isoformat()
            ok, msg = save_parameters_to_fb(email, idt, preset_name, payload)
            if ok:
                st.sidebar.success(f"Preset '{preset_name}' tersimpan.")
            else:
                st.sidebar.error(f"Gagal menyimpan preset: {msg}")

# fetch presets for this user (if logged)
presets = {}
idt = st.session_state.get("idToken")
email = st.session_state.get("email")
if idt and email and FIREBASE_DB_URL:
    presets_dict, err = list_presets_from_fb(email, idt)
    if presets_dict is None:
        st.sidebar.warning("Tidak dapat mengambil presets.")
    else:
        presets = presets_dict
else:
    presets = {}

preset_list = ["-- Select preset --"] + sorted(list(presets.keys()))
sel_preset = st.sidebar.selectbox("Saved presets", preset_list, key="sel_preset")

colL, colR = st.sidebar.columns([1,1])

with colL:
    if st.button("📂 Load Parameter"):
        if sel_preset == "-- Select preset --":
            st.sidebar.error("Pilih preset terlebih dahulu.")
        else:
            idt = st.session_state.get("idToken")
            email = st.session_state.get("email")
            if not idt or not email:
                st.sidebar.error("Auth token tidak ada. Silakan logout & login ulang.")
            else:
                data_json, err = load_preset_from_fb(email, idt, sel_preset)
                if data_json is None:
                    st.sidebar.error(f"Gagal load preset: {err}")
                else:
                    # when loading: fill COMMON + mode-specific keys only, set others to default
                    # We respect the mode stored in preset if present, but user must keep current app mode as desired.
                    # We'll load keys matching current *app* mode (not forcing mode change).
                    mode_keys = OWNER_KEYS if mode == "Owner" else CHARTER_KEYS
                    keys_to_apply = COMMON_KEYS + mode_keys + MAIN_INPUT_KEYS
                    defaults = _defaults_for_keys(keys_to_apply)
                    for k in keys_to_apply:
                        dv = data_json.get(k, defaults[k])
                        try:
                            st.session_state[k] = dv
                        except Exception:
                            # ignore problematic keys
                            pass
                    # ensure keys that are NOT in keys_to_apply are reset to defaults (so only selected group shows)
                    other_keys = set(OWNER_KEYS + CHARTER_KEYS) - set(mode_keys)
                    for k in other_keys:
                        try:
                            st.session_state[k] = _defaults_for_keys([k])[k]
                        except Exception:
                            pass
                    st.success(f"Preset '{sel_preset}' dimuat. (Mode saat ini: {mode})")
                    st.rerun()

with colR:
    if st.button("🗑️ Delete Parameter"):
        if sel_preset == "-- Select preset --":
            st.sidebar.error("Pilih preset untuk dihapus.")
        else:
            idt = st.session_state.get("idToken")
            email = st.session_state.get("email")
            if not idt or not email:
                st.sidebar.error("Auth token tidak ada. Silakan logout & login ulang.")
            else:
                ok, msg = delete_preset_from_fb(email, idt, sel_preset)
                if ok:
                    st.sidebar.success(f"Preset '{sel_preset}' dihapus.")
                    st.rerun()
                else:
                    st.sidebar.error(f"Gagal menghapus preset: {msg}")

# Reset button: kosongkan semua sidebar parameter (ke default)
if st.sidebar.button("🔄 Reset Parameter (kosongkan)"):
    all_keys = COMMON_KEYS + OWNER_KEYS + CHARTER_KEYS + MAIN_INPUT_KEYS + ["port_pol","port_pod","next_port"]
    defaults = _defaults_for_keys(all_keys)
    for k in all_keys:
        try:
            st.session_state[k] = defaults[k]
        except Exception:
            pass
    st.sidebar.success("Parameter sidebar dikosongkan.")
    st.rerun()

# ===== PERHITUNGAN =====
if st.button("Calculate Freight 💸"):
    try:
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_voyage_days_round = int(total_voyage_days) if total_voyage_days % 1 < 0.5 else int(total_voyage_days) + 1

        total_consumption_fuel = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * total_voyage_days_round
        cost_fw = total_consumption_fw * price_fw
        cost_fuel = total_consumption_fuel * price_fuel

        charter_cost = (charter / 30) * total_voyage_days
        crew_cost = (crew / 30) * total_voyage_days if mode == "Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode == "Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode == "Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode == "Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode == "Owner" else 0
        premi_cost = distance_pol_pod * premi_nm
        port_cost = port_cost_pol + port_cost_pod + asist_tug

        total_cost = sum([
            charter_cost, crew_cost, insurance_cost, docking_cost, maintenance_cost, certificate_cost,
            premi_cost, port_cost, cost_fuel, cost_fw, other_cost
        ])

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # Freight Price Calculation
        revenue_user = freight_price_input * qyt_cargo
        pph_user = revenue_user * 0.012
        profit_user = revenue_user - total_cost - pph_user
        profit_percent_user = (profit_user / revenue_user * 100) if revenue_user > 0 else 0

        # ===== DISPLAY RESULTS =====
        st.subheader("📋 Calculation Results")
        st.markdown(f"""
**Type Cargo:** {type_cargo}  
**Cargo Quantity:** {qyt_cargo:,.0f} {type_cargo.split()[1]}  
**Distance (NM):** {distance_pol_pod:,.0f}  

**Total Voyage (Days):** {total_voyage_days:.2f}  
**Total Sailing Time (Hour):** {sailing_time:.2f}  
**Total Consumption Fuel (Ltr):** {total_consumption_fuel:,.0f}  
**Total Consumption Freshwater (Ton):** {total_consumption_fw:,.0f}  

**Fuel Cost (Rp):** Rp {cost_fuel:,.0f}  
**Freshwater Cost (Rp):** Rp {cost_fw:,.0f}  
""")

        # Costs summary
        if mode == "Owner":
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

        for k, v in owner_data.items():
            st.markdown(f"- {k}: Rp {v:,.0f}")

        st.markdown(f"**🧮 Total Cost:** Rp {total_cost:,.0f}")
        st.markdown(f"**🧮 Freight Cost ({type_cargo.split()[1]}):** Rp {freight_cost_mt:,.0f}")

        # Freight price section (only show if filled)
        if freight_price_input > 0:
            st.subheader("💰 Freight Price Calculation User")
            st.markdown(f"""
**Freight Price (Rp/MT):** Rp {freight_price_input:,.0f}  
**Revenue:** Rp {revenue_user:,.0f}  
**PPH 1.2%:** Rp {pph_user:,.0f}  
**Profit:** Rp {profit_user:,.0f}  
**Profit %:** {profit_percent_user:.2f} %
""")

        # Profit scenario (always shown)
        data = []
        for p in range(0, 55, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"Rp {freight_persen:,.0f}", f"Rp {revenue:,.0f}", f"Rp {pph:,.0f}", f"Rp {profit:,.0f}"])
        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
        st.subheader("💹 Profit Scenario 0–50%")
        st.dataframe(df_profit, use_container_width=True)

        # ===== PDF GENERATOR (tidak diubah fungsinya) =====
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("<b>Freight Calculator Report</b>", styles['Title']))
            elements.append(Spacer(1, 6))

            # Voyage Information
            elements.append(Paragraph("<b>Voyage Information</b>", styles['Heading3']))
            voyage_data = [
                ["Port Of Loading", port_pol],
                ["Port Of Discharge", port_pod],
                ["Next Port", next_port],
                ["Cargo Quantity", f"{qyt_cargo:,.0f} {type_cargo.split()[1]}"],
                ["Distance (NM)", f"{distance_pol_pod:,.0f}"],
                ["Total Voyage (Days)", f"{total_voyage_days:.2f}"]
            ]
            t_voyage = Table(voyage_data, hAlign='LEFT', colWidths=[150, 280])
            t_voyage.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
            elements.append(t_voyage)
            elements.append(Spacer(1, 6))

            # Calculation Results
            elements.append(Paragraph("<b>Calculation Results</b>", styles['Heading3']))
            calc_data = [
                ["Total Sailing Time (Hour)", f"{sailing_time:.2f}"],
                ["Total Consumption Fuel (Ltr)", f"{total_consumption_fuel:,.0f} Ltr"],
                ["Total Consumption Freshwater (Ton)", f"{total_consumption_fw:,.0f} Ton"],
                ["Fuel Cost (Rp)", f"Rp {cost_fuel:,.0f}"],
                ["Freshwater Cost (Rp)", f"Rp {cost_fw:,.0f}"]
            ]
            for k, v in owner_data.items():
                calc_data.append([k, f"Rp {v:,.0f}"])
            calc_data.append(["Total Cost (Rp)", f"Rp {total_cost:,.0f}"])
            calc_data.append([f"Freight Cost ({type_cargo.split()[1]})", f"Rp {freight_cost_mt:,.0f}"])
            t_calc = Table(calc_data, hAlign='LEFT', colWidths=[200, 200])
            t_calc.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
            elements.append(t_calc)
            elements.append(Spacer(1, 6))

            # Freight Price Calculation User (only if provided)
            if freight_price_input > 0:
                elements.append(Paragraph("<b>Freight Price Calculation User</b>", styles['Heading3']))
                fpc_data = [
                    ["Freight Price (Rp/MT)", f"Rp {freight_price_input:,.0f}"],
                    ["Revenue", f"Rp {revenue_user:,.0f}"],
                    ["PPH 1.2%", f"Rp {pph_user:,.0f}"],
                    ["Profit", f"Rp {profit_user:,.0f}"],
                    ["Profit %", f"{profit_percent_user:.2f} %"]
                ]
                t_fpc = Table(fpc_data, hAlign='LEFT', colWidths=[200, 200])
                t_fpc.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
                elements.append(t_fpc)
                elements.append(Spacer(1, 6))

            # Profit Scenario (always)
            elements.append(Paragraph("<b>Profit Scenario 0–50%</b>", styles['Heading3']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t_profit = Table(profit_table, hAlign='LEFT', colWidths=[60, 110, 110, 110, 110])
            t_profit.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
            elements.append(t_profit)
            elements.append(Spacer(1, 6))

            elements.append(Paragraph(f"<i>Generated By: https://freight-calculatordemo2.streamlit.app/</i>", styles['Normal']))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf()
        safe_pol = port_pol.replace(" ", "_") if port_pol else "POL"
        safe_pod = port_pod.replace(" ", "_") if port_pod else "POD"
        file_name = f"Freight_Report_{safe_pol}_{safe_pod}_{datetime.now():%Y%m%d}.pdf"

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")

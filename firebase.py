import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# 🔐 LOAD SECRETS (WAJIB AMAN)
# =========================
if "firebase" not in st.secrets:
    st.error("❌ firebase secrets tidak ditemukan di Streamlit")
    st.stop()

firebase = st.secrets["firebase"]

# =========================
# 🔥 VALIDASI DB URL
# =========================
DB_URL = firebase.get("FIREBASE_DB_URL", "").strip()

if not DB_URL:
    st.error("❌ FIREBASE_DB_URL kosong / tidak terbaca")
    st.stop()

# =========================
# 🔥 BUILD SERVICE ACCOUNT SAFE
# =========================
try:
    firebase_config = {
        "type": firebase["type"],
        "project_id": firebase["project_id"],
        "private_key": firebase["private_key"].replace("\\n", "\n"),
        "client_email": firebase["client_email"],
        "token_uri": firebase["token_uri"]
    }
except Exception as e:
    st.error(f"❌ Firebase config error: {e}")
    st.stop()

# =========================
# 🚀 INIT FIREBASE (ONLY ONCE)
# =========================
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_config)

        firebase_admin.initialize_app(cred, {
            "databaseURL": DB_URL
        })

    except Exception as e:
        st.error(f"❌ Firebase init gagal: {e}")
        st.stop()

# =========================
# 🌐 GET REF (AMAN)
# =========================
def get_ref():
    try:
        return db.reference("/")
    except Exception as e:
        st.error(f"❌ Firebase DB reference error: {e}")
        st.stop()

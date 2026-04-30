import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# 🔐 LOAD SECRETS
# =========================
firebase = st.secrets["firebase"]
database = st.secrets["database"]

# =========================
# 🔥 DB URL (SEPARATE SECTION)
# =========================
DB_URL = database["FIREBASE_DB_URL"].strip()

if not DB_URL:
    st.error("❌ FIREBASE_DB_URL kosong")
    st.stop()

# =========================
# 🔥 SERVICE ACCOUNT
# =========================
firebase_config = {
    "type": firebase["type"],
    "project_id": firebase["project_id"],
    "private_key": firebase["private_key"].replace("\\n", "\n"),
    "client_email": firebase["client_email"],
    "token_uri": firebase["token_uri"]
}

# =========================
# 🚀 INIT FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)

    firebase_admin.initialize_app(cred, {
        "databaseURL": DB_URL
    })

# =========================
# 🌐 GET REF
# =========================
def get_ref():
    return db.reference("/")

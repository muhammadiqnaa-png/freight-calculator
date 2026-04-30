import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# 🔐 LOAD FIREBASE CONFIG
# =========================
firebase = st.secrets.get("firebase")

if firebase is None:
    st.error("Firebase secrets tidak ditemukan")
    st.stop()

# =========================
# 🔥 VALIDASI DB URL (IMPORTANT)
# =========================
DB_URL = firebase.get("FIREBASE_DB_URL")

if not DB_URL:
    st.error("❌ FIREBASE_DB_URL kosong / tidak terbaca dari secrets")
    st.stop()

# =========================
# 🔥 BUILD CREDENTIAL
# =========================
firebase_config = dict(firebase)
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")

# =========================
# 🚀 INIT FIREBASE APP
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)

    firebase_admin.initialize_app(cred, {
        "databaseURL": DB_URL
    })

# =========================
# 🌐 DB REFERENCE
# =========================
ref = db.reference("/")

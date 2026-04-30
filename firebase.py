import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# 🔐 LOAD SECRETS SAFELY
# =========================
firebase = st.secrets.get("firebase")

if not firebase:
    st.error("❌ Firebase secrets tidak ditemukan")
    st.stop()

# =========================
# 🔥 AMBIL DB URL (WAJIB VALIDASI)
# =========================
DB_URL = firebase.get("FIREBASE_DB_URL")

if not DB_URL or DB_URL.strip() == "":
    st.error("❌ FIREBASE_DB_URL kosong saat runtime")
    st.stop()

# =========================
# 🔥 COPY CONFIG
# =========================
firebase_config = dict(firebase)

# FIX PRIVATE KEY
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")

# =========================
# 🚀 INIT FIREBASE (ONLY ONCE)
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

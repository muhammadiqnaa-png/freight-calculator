import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# 🔐 LOAD SECRETS
# =========================
firebase = st.secrets.get("firebase")

if firebase is None:
    st.error("❌ Firebase secrets tidak ditemukan")
    st.stop()

# =========================
# 🔥 DB URL (FIX UTAMA)
# =========================
DB_URL = firebase.get("FIREBASE_DB_URL")

if not DB_URL:
    st.error("❌ FIREBASE_DB_URL kosong / tidak terbaca")
    st.stop()

# =========================
# 🔥 SERVICE ACCOUNT CONFIG
# =========================
firebase_config = dict(firebase)
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")

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

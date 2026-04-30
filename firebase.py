import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# 🔐 LOAD FIREBASE SECRETS
# =========================
try:
    firebase = st.secrets["firebase"]
except Exception:
    st.error("❌ Secrets [firebase] tidak ditemukan")
    st.stop()

# =========================
# 🔥 AMBIL DB URL DENGAN AMAN
# =========================
DB_URL = firebase.get("FIREBASE_DB_URL")

if not DB_URL:
    st.error("❌ FIREBASE_DB_URL kosong / tidak terbaca")
    st.stop()

# =========================
# 🔥 COPY CONFIG SAFE
# =========================
firebase_config = dict(firebase)

# FIX PRIVATE KEY
if "private_key" in firebase_config:
    firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")
else:
    st.error("❌ private_key tidak ditemukan")
    st.stop()

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

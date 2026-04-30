import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# 🔐 LOAD SECRETS
# =========================
if "firebase" not in st.secrets:
    st.error("❌ Firebase secrets tidak ditemukan")
    st.stop()

firebase = dict(st.secrets["firebase"])

# =========================
# 🔥 FIX PRIVATE KEY (WAJIB)
# =========================
if "private_key" not in firebase:
    st.error("❌ private_key tidak ada di secrets")
    st.stop()

firebase["private_key"] = firebase["private_key"].replace("\\n", "\n")

# =========================
# 🔥 VALIDATE DB URL
# =========================
DB_URL = firebase.get("FIREBASE_DB_URL")

if not DB_URL:
    st.error("❌ FIREBASE_DB_URL kosong")
    st.stop()

# =========================
# 🚀 INIT FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase)

    firebase_admin.initialize_app(cred, {
        "databaseURL": DB_URL
    })

# =========================
# 🌐 DB REFERENCE
# =========================
def get_ref():
    return db.reference("/")

import streamlit as st

# =========================
# 🔐 FIREBASE CONFIG SAFE LOAD
# =========================
firebase = st.secrets.get("firebase", None)

if firebase is None:
    st.error("❌ Firebase secrets tidak ditemukan. Cek Streamlit Secrets [firebase]")
    st.stop()

FIREBASE_API_KEY = firebase.get("FIREBASE_API_KEY", "")
FIREBASE_DB_URL = firebase.get("FIREBASE_DB_URL", "")
FIREBASE_PROJECT_ID = firebase.get("FIREBASE_PROJECT_ID", "")
FIREBASE_CLIENT_EMAIL = firebase.get("FIREBASE_CLIENT_EMAIL", "")
FIREBASE_PRIVATE_KEY = firebase.get("FIREBASE_PRIVATE_KEY", "")

# =========================
# 🔥 FIREBASE INIT
# =========================
import firebase_admin
from firebase_admin import credentials, db

# prevent double init (Streamlit reload safety)
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": FIREBASE_PROJECT_ID,
        "private_key_id": "dummy",
        "private_key": FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
        "client_email": FIREBASE_CLIENT_EMAIL,
        "client_id": "dummy",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "dummy"
    })

    firebase_admin.initialize_app(cred, {
        "databaseURL": FIREBASE_DB_URL
    })

# =========================
# 📦 FIREBASE REF
# =========================
ref = db.reference("/")

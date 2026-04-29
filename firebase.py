import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# INIT FIREBASE (SAFE)
# =========================

if not firebase_admin._apps:

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": st.secrets["firebase"]["FIREBASE_PROJECT_ID"],
        "private_key": st.secrets["firebase"]["FIREBASE_PRIVATE_KEY"].
        "client_email": st.secrets["firebase"]["FIREBASE_CLIENT_EMAIL"],
        "token_uri": "https://oauth2.googleapis.com/token"
    })

    firebase_admin.initialize_app(cred, {
        "databaseURL": st.secrets["firebase"]["FIREBASE_DB_URL"]
    })


# =========================
# REFERENCE ROOT DB
# =========================
ref = db.reference("/")

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

firebase = st.secrets["firebase"]

# 🔥 FIX PRIVATE KEY (INI KUNCI UTAMA)
private_key = firebase["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n")

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": firebase["FIREBASE_PROJECT_ID"],
    "private_key": private_key,
    "client_email": firebase["FIREBASE_CLIENT_EMAIL"],
    "token_uri": "https://oauth2.googleapis.com/token"
})

# 🔥 prevent double init (WAJIB)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase["FIREBASE_DB_URL"]
    })

ref = db.reference("/")

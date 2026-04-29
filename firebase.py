import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# ===== BUILD CREDENTIAL MANUAL DARI SECRETS =====
cred_dict = {
    "type": "service_account",
    "project_id": st.secrets["FIREBASE_PROJECT_ID"],
    "private_key_id": "dummy",
    "private_key": st.secrets["FIREBASE_PRIVATE_KEY"],
    "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
    "token_uri": "https://oauth2.googleapis.com/token"
}

cred = credentials.Certificate(cred_dict)

# ===== INIT FIREBASE =====
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": st.secrets["FIREBASE_DB_URL"]
    })

ref = db.reference("/")

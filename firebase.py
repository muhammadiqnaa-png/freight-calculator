import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

# ===== INIT FIREBASE =====
if not firebase_admin._apps:

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": st.secrets["FIREBASE_PROJECT_ID"],
        "private_key": st.secrets["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
    })

    firebase_admin.initialize_app(cred, {
        "databaseURL": st.secrets["FIREBASE_DB_URL"]
    })

ref = db.reference("/")

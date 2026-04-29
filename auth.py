import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# ambil semua secrets dari section firebase
firebase = st.secrets["firebase"]

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": firebase["FIREBASE_PROJECT_ID"],
    "private_key": firebase["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
    "client_email": firebase["FIREBASE_CLIENT_EMAIL"],
})

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase["FIREBASE_DB_URL"]
    })

ref = db.reference("/")

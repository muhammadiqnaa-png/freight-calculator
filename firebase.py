import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import json

# =========================
# LOAD RAW JSON STRING
# =========================
firebase_json = json.loads(st.secrets["firebase_json"])

# =========================
# INIT FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_json)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_json.get("databaseURL")
    })

def get_ref(path):
    return db.reference(path)

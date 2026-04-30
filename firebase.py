import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# LOAD SECRETS
# =========================
firebase_dict = dict(st.secrets["firebase"])

# FIX PRIVATE KEY FORMAT
firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")

# =========================
# INIT FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_dict["databaseURL"]
    })


# =========================
# GET REFERENCE FUNCTION
# =========================
def get_ref(path):
    return db.reference(path)

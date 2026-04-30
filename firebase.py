import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

# =========================
# LOAD FIREBASE SECRETS
# =========================
firebase_dict = dict(st.secrets["firebase"])

# 🔥 FIX IMPORTANT: ubah \n jadi newline asli
firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")

# =========================
# INIT FIREBASE (SAFE)
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_dict.get("databaseURL")
    })

# =========================
# FUNCTION REF
# =========================
def get_ref(path):
    return db.reference(path)

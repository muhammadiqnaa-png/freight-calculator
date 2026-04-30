import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import json

# =========================
# LOAD SECRETS
# =========================
firebase_dict = dict(st.secrets["firebase"])

# =========================
# FIX PRIVATE KEY
# =========================
firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n").strip()

# =========================
# 🔥 CONVERT KE JSON CLEAN (FIX STABILITY ISSUE)
# =========================
firebase_json = json.loads(json.dumps(firebase_dict))

# =========================
# INIT FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_json)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_dict.get("databaseURL")
    })

# =========================
# REF FUNCTION
# =========================
def get_ref(path):
    return db.reference(path)

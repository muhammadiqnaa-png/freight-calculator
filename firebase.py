import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

# =========================
# LOAD SECRETS
# =========================
firebase_dict = dict(st.secrets["firebase"])

# =========================
# 🔥 FORCE FIX PRIVATE KEY (IMPORTANT)
# =========================
key = firebase_dict["private_key"]

# double safety fix (ini penting banget)
key = key.replace("\\n", "\n")
key = key.replace("\n\n", "\n").strip()

firebase_dict["private_key"] = key

# =========================
# DEBUG CHECK (biar pasti)
# =========================
if "BEGIN PRIVATE KEY" not in firebase_dict["private_key"]:
    raise ValueError("Private key rusak / tidak valid PEM format")

# =========================
# INIT FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_dict.get("databaseURL")
    })


def get_ref(path):
    return db.reference(path)

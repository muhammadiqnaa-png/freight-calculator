import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# 🔐 LOAD SECRETS
# =========================
firebase = dict(st.secrets["firebase"])

# fix private key
firebase["private_key"] = firebase["private_key"].replace("\\n", "\n")

# =========================
# 🚀 INIT FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase["FIREBASE_DB_URL"]
    })

# =========================
# 🌐 DB REF
# =========================
def get_ref():
    return db.reference("/")

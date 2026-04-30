import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db

# =========================
# 🔐 LOAD FIREBASE CONFIG
# =========================
firebase = st.secrets.get("firebase", None)

if firebase is None:
    st.error("❌ Firebase secrets tidak ditemukan")
    st.stop()

# =========================
# 🔥 BUILD CREDENTIAL PROPERLY
# =========================
firebase_config = dict(firebase)

# fix private key newline issue
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")

# =========================
# 🚀 INIT FIREBASE (SAFE)
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase.get("FIREBASE_DB_URL")
    })

# =========================
# 👤 REGISTER USER
# =========================
def register_user(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        return True, user.uid
    except Exception as e:
        return False, str(e)

# =========================
# ⚠️ LOGIN NOTE (IMPORTANT)
# =========================
def login_user(email, password):
    return False, "Firebase Admin tidak support login password. Gunakan Firebase Auth client SDK (frontend) atau verify ID token."

import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db

# =========================
# 🔐 LOAD SECRETS
# =========================
firebase = st.secrets.get("firebase")

if not firebase:
    st.error("❌ Firebase secrets tidak ditemukan")
    st.stop()

# =========================
# 🔥 INIT FIREBASE (SAFE)
# =========================
if not firebase_admin._apps:

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": firebase["FIREBASE_PROJECT_ID"],
        "private_key_id": "dummy",
        "private_key": firebase["FIREBASE_PRIVATE_KEY"],
        "client_email": firebase["FIREBASE_CLIENT_EMAIL"],
        "client_id": "dummy",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "dummy"
    })

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase["FIREBASE_DB_URL"]
    })

ref = db.reference("/")

# =========================
# 👤 REGISTER USER
# =========================
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return True, user.uid
    except Exception as e:
        return False, str(e)

# =========================
# 🔐 LOGIN USER
# =========================
def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        return True, user.uid
    except auth.UserNotFoundError:
        return False, "Email tidak ditemukan"
    except Exception as e:
        return False, str(e)

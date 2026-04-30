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
        "private_key": firebase["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": firebase["FIREBASE_CLIENT_EMAIL"],
        "token_uri": "https://oauth2.googleapis.com/token"
    })

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase["FIREBASE_DB_URL"]
    })

# =========================
# 📡 DB REFERENCE
# =========================
ref = db.reference("/")

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
# 🔐 LOGIN USER (SIMPLIFIED)
# =========================
def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        return True, user.uid
    except auth.UserNotFoundError:
        return False, "Email tidak ditemukan"
    except Exception as e:
        return False, str(e)

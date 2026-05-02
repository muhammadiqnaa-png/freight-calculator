import streamlit as st
import requests

# =========================
# 🔐 AMBIL API KEY (AMAN)
# =========================
def get_api_key():
    api_key = st.secrets.get("FIREBASE_API_KEY")
    if not api_key:
        st.error("❌ FIREBASE_API_KEY belum diset di secrets")
        st.stop()
    return api_key


# =========================
# 🔑 LOGIN USER
# =========================
def login_user(email, password):
    api_key = get_api_key()

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        res = requests.post(url, json=payload)
        data = res.json()

        if res.status_code == 200:
            return True, data
        else:
            error_msg = data.get("error", {}).get("message", "Login gagal")
            return False, error_msg

    except Exception as e:
        return False, str(e)


# =========================
# 📝 REGISTER USER
# =========================
def register_user(email, password):
    api_key = get_api_key()

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        res = requests.post(url, json=payload)
        data = res.json()

        if res.status_code == 200:
            return True, data
        else:
            error_msg = data.get("error", {}).get("message", "Register gagal")
            return False, error_msg

    except Exception as e:
        return False, str(e)

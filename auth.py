import streamlit as st
import requests

# =========================
# 🔐 REGISTER USER
# =========================
def register_user(email, password):
    api_key = st.secrets["firebase"]["FIREBASE_API_KEY"]

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"

    res = requests.post(url, json={
        "email": email,
        "password": password,
        "returnSecureToken": True
    })

    if res.status_code == 200:
        return True, res.json()["localId"]
    else:
        return False, res.json()["error"]["message"]


# =========================
# 🔐 LOGIN USER
# =========================
def login_user(email, password):
    api_key = st.secrets["firebase"]["FIREBASE_API_KEY"]

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

    res = requests.post(url, json={
        "email": email,
        "password": password,
        "returnSecureToken": True
    })

    if res.status_code == 200:
        return True, res.json()["localId"]
    else:
        return False, res.json()["error"]["message"]

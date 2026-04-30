import streamlit as st
import requests

# ====== FIREBASE AUTH ======
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]
AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
REGISTER_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

def login_user(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def register_user(email, password):
    res = requests.post(REGISTER_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()


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

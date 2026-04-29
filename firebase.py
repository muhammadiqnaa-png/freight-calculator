import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json

firebase_json = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])

cred = credentials.Certificate(firebase_json)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": st.secrets["firebase"]["FIREBASE_DB_URL"]
    })

ref = db.reference("/")

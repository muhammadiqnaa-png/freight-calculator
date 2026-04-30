import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

firebase = st.secrets["firebase"]

if not firebase_admin._apps:
    cred = credentials.Certificate(dict(firebase))
    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase["databaseURL"]
    })

ref = db.reference()

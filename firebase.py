import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

firebase_dict = dict(st.secrets["firebase"])

# FIX safety (biar tidak error escape)
firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_dict.get("databaseURL")
    })

def get_ref(path):
    return db.reference(path)

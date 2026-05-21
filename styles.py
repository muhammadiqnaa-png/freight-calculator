import streamlit as st

def load_css():

    st.markdown("""
    <style>

    /* Base font */
    html, body, [class*="css"]  {
        font-size: 13px !important;
    }

    /* Label */
    label {
        font-size: 12px !important;
    }

    /* Input text & number */
    input, select {
        font-size: 13px !important;
    }

    /* Button */
    button {
        font-size: 13px !important;
        padding: 6px 10px !important;
    }

    /* Metric / big text */
    h1, h2, h3 {
        font-size: 16px !important;
    }

    /* Caption kecil */
    .small-text {
        font-size: 11px !important;
        color: #666;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>

    /* 🔥 BUTTON CALCULATE UTAMA */
    div.stButton > button {
        background: linear-gradient(135deg, #6495ED, #FFFFFF, #6495ED);
        color: Black;
        font-weight: bold;
        border-radius: 12px;
        height: 48px;
        font-size: 14px;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    }

    /* 🔥 EFFECT HOVER */
    div.stButton > button:hover {
        background: linear-gradient(135deg, #6495ED, #FFFFFF, #6495ED);
        color: Black;
        font-weight: bold;
        border-radius: 12px;
        height: 48px;
        font-size: 14px;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    }

    /* 🔥 BIAR ADA JARAK DI HP */
    div.stButton {
        margin-top: 10px;
        margin-bottom: 10px;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>

    /* ===== FIX RESULT BOX DARK MODE ===== */

    div[data-testid="stAlert"] {
        color: white !important;
    }

    /* SUCCESS */
    div[data-testid="stAlert"][kind="success"] {
        background-color: #1b5e20 !important;
        border-left: 5px solid #00e676 !important;
    }

    /* WARNING */
    div[data-testid="stAlert"][kind="warning"] {
        background-color: #ff8f00 !important;
        border-left: 5px solid #ffd54f !important;
    }

    /* ERROR */
    div[data-testid="stAlert"][kind="error"] {
        background-color: #b71c1c !important;
        border-left: 5px solid #ff5252 !important;
    }

    /* FORCE TEXT ALWAYS VISIBLE */
    html, body, [class*="css"] {
        color: #f5f5f5 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>

    /* ===== LOGIN BUTTON (BIRU) ===== */
    div.stButton > button[kind="primary"] {
        background: #2563eb !important;
        color: white !important;
        border-radius: 10px !important;
        height: 42px !important;
        font-weight: 600 !important;
        border: none !important;
    }

    /* hover login */
    div.stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
    }

    /* ===== CREATE ACCOUNT (KOTAK POLOS) ===== */
    div.stButton > button[kind="secondary"] {
        background: transparent !important;
        color: #2563eb !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        height: 42px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }

    /* hover tetap soft */
    div.stButton > button[kind="secondary"]:hover {
        background: #f8fafc !important;
        border-color: #2563eb !important;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>

    /* ===== CONTAINER ===== */
    div[role="radiogroup"] {
        display: flex;
        gap: 8px;
        width: 100%;
    }

    /* ===== DEFAULT OPTION ===== */
    div[role="radiogroup"] label {
        flex: 1;
        text-align: center;
        padding: 8px 10px;
        border-radius: 10px;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 12px;
        color: #334155;
    }

    /* hide radio dot */
    div[role="radiogroup"] input {
        display: none;
    }

    /* 🔥 ACTIVE (SELECTED) */
    div[role="radiogroup"] label:has(input:checked) {
        background: #2563eb !important;
        color: white !important;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(37,99,235,0.35);
        transform: scale(1.05);
        border: none;
    }

    /* hover */
    div[role="radiogroup"] label:hover {
        background: #e2e8f0;
    }

    </style>
    """, unsafe_allow_html=True)

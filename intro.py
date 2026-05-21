import streamlit as st

def show_intro(cookies):

    # ===== INTRO STATE =====
    if "hide_intro" not in st.session_state:
        st.session_state.hide_intro = False

    # ambil dari cookies (persist)
    if cookies.get("hide_intro") == "true":
        st.session_state.hide_intro = True

    # ==========================================================
    # 🚀 INTRO / ONBOARDING SCREEN
    # ==========================================================
    if not st.session_state.hide_intro:

        # 🔥 Biar posisi lebih tengah (mobile friendly)
        st.markdown("""
        <style>
        .block-container {
            padding-top: 5vh;
            padding-bottom: 5vh;
        }
        </style>
        """, unsafe_allow_html=True)

        # ===== UI INTRO =====
        st.markdown("""
        <div style="
            text-align:center;
            padding:50px 25px;
        ">

        <h1 style="
            font-size:28px;
            font-weight:800;
            margin-bottom:5px;
        ">
            🚢 Welcome Freight Calculator
        </h1>

        <p style="
            font-size:13px;
            color:#64748B;
            margin-bottom:20px;
        ">
            Cost, Freight & Profit Analysis Tool
        </p>

        <div style="
            display:grid;
            grid-template-columns: repeat(2, 1fr);
            gap:12px;
            margin-top:10px;
            font-size:12px;
        ">

        <div style="
            background:linear-gradient(135deg,#e0f2fe,#f8fafc);
            padding:12px;
            border-radius:12px;
            font-weight:500;
        ">
            ⚡ Cepat
        </div>

        <div style="
            background:linear-gradient(135deg,#e0f2fe,#f8fafc);
            padding:12px;
            border-radius:12px;
            font-weight:500;
        ">
            🎯 Akurat
        </div>

        <div style="
            background:linear-gradient(135deg,#e0f2fe,#f8fafc);
            padding:12px;
            border-radius:12px;
            font-weight:500;
        ">
            💰 Hitung untung/rugi
        </div>

        <div style="
            background:linear-gradient(135deg,#e0f2fe,#f8fafc);
            padding:12px;
            border-radius:12px;
            font-weight:500;
        ">
            🤝🏻 Nego lebih percaya diri
        </div>

        </div>

        <div style="
            margin-top:30px;
            font-size:11px;
            color:#94a3b8;
        ">
            Built with ❤️ by <b style="color:#2563eb;">Muhammad Iqna</b>
        </div>

        </div>
        """, unsafe_allow_html=True)

        # ===== CHECKBOX =====
        dont_show = st.checkbox("Jangan tampilkan lagi")

        # ===== BUTTON =====
        if st.button("🚀 Get Started", use_container_width=True):

            if dont_show:
                cookies["hide_intro"] = "true"
                cookies.save()

            st.session_state.hide_intro = True
            st.session_state.page = "login"
            st.rerun()

        st.stop()

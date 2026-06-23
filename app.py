import streamlit as st
import os
from datetime import datetime

from smtp_finder import load_combos_by_domain, bruteforce_domain

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="KRANOS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PREMIUM APPLE STYLE UI
# =========================================================

st.markdown("""
<style>

/* =========================================================
BACKGROUND
========================================================= */

.stApp {

    background:
    linear-gradient(
        rgba(0,0,0,0.45),
        rgba(0,0,0,0.55)
    ),
    url("https://images.unsplash.com/photo-1506744038136-46273834b3fb");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* =========================================================
HIDE STREAMLIT
========================================================= */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* cache Deploy button seulement */
.stDeployButton {
    display: none !important;
}

/* IMPORTANT : garder le header visible */
header {
    visibility: visible;
}

/* =========================================================
GLOBAL
========================================================= */

html, body, [class*="css"]  {

    font-family:
    -apple-system,
    BlinkMacSystemFont,
    "SF Pro Display",
    sans-serif;
}

.block-container {

    padding-top: 2rem;
    padding-left: 4rem;
    padding-right: 4rem;
    padding-bottom: 2rem;
}

/* =========================================================
HEADER
========================================================= */

.hero-title {

    font-size: 72px;
    font-weight: 300;

    color: white;

    letter-spacing: 2px;

    margin-bottom: 10px;

    text-shadow: 0 4px 30px rgba(0,0,0,0.35);
}

.hero-subtitle {

    color: rgba(255,255,255,0.82);

    font-size: 20px;

    font-weight: 300;

    margin-bottom: 40px;
}

/* =========================================================
GLASSMORPHISM CARD
========================================================= */

.glass {

    background: rgba(20,20,20,0.55);

    backdrop-filter: blur(25px);

    -webkit-backdrop-filter: blur(25px);

    border: 1px solid rgba(255,255,255,0.12);

    border-radius: 28px;

    padding: 28px;

    box-shadow:
        0 8px 32px rgba(0,0,0,0.35);

    transition: 0.3s ease;
}

.glass:hover {

    transform: translateY(-2px);

    box-shadow:
        0 15px 45px rgba(0,0,0,0.45);
}

/* =========================================================
SECTION TITLES
========================================================= */

.section-title {

    color: white;

    font-size: 20px;

    font-weight: 500;

    margin-bottom: 18px;

    letter-spacing: 1px;
}

/* =========================================================
CONSOLE
========================================================= */

.console {

    background: rgba(0,0,0,0.42);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 18px;

    padding: 22px;

    height: 520px;

    overflow-y: auto;

    color: #ffffff;

    font-family: "SF Mono", monospace;

    font-size: 14px;

    line-height: 1.8;

    backdrop-filter: blur(12px);
}

/* =========================================================
METRIC
========================================================= */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.06);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 18px;

    padding: 20px;

    backdrop-filter: blur(15px);
}

[data-testid="stMetricValue"] {

    color: white;

    font-size: 48px;

    font-weight: 700;
}

[data-testid="stMetricLabel"] {

    color: rgba(255,255,255,0.72);

    font-size: 15px;
}

/* =========================================================
BUTTONS
========================================================= */

.stButton > button {

    width: 100%;

    height: 56px;

    border: none;

    border-radius: 16px;

    background: rgba(255,255,255,0.95);

    color: black;

    font-size: 15px;

    font-weight: 600;

    transition: 0.3s ease;

    box-shadow:
        0 8px 25px rgba(255,255,255,0.12);
}

.stButton > button:hover {

    transform: scale(1.02);

    background: white;

    box-shadow:
        0 12px 35px rgba(255,255,255,0.22);
}

/* =========================================================
UPLOAD
========================================================= */

[data-testid="stFileUploader"] {

    background: rgba(255,255,255,0.06);

    border-radius: 18px;

    padding: 15px;

    border: 1px solid rgba(255,255,255,0.08);
}

/* =========================================================
HITS
========================================================= */

.hit-card {

    background: rgba(20,20,20,0.58);

    backdrop-filter: blur(20px);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 20px;

    padding: 24px;

    margin-bottom: 18px;

    color: white;

    line-height: 1.8;
}

/* =========================================================
SCROLLBAR
========================================================= */

::-webkit-scrollbar {

    width: 8px;
}

::-webkit-scrollbar-track {

    background: transparent;
}

::-webkit-scrollbar-thumb {

    background: rgba(255,255,255,0.22);

    border-radius: 20px;
}

/* =========================================================
MOBILE RESPONSIVE
========================================================= */

@media (max-width: 768px) {

    .block-container {

        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
    }

    .hero-title {

        font-size: 42px;
    }

    .hero-subtitle {

        font-size: 15px;
    }

    .console {

        height: 320px;
        font-size: 12px;
    }

    [data-testid="stMetricValue"] {

        font-size: 34px;
    }

    .glass {

        padding: 18px;
        border-radius: 20px;
    }

    .stButton > button {

        height: 50px;
        font-size: 14px;
    }
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero-title">
KRANOS
</div>

<div class="hero-subtitle">
Professional SMTP Audit Platform
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## Configuration")

    uploaded_file = st.file_uploader(
        "Upload combo file",
        type=["txt"]
    )

    if uploaded_file:

        with open("temp_combo.txt", "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("File uploaded successfully")

# =========================================================
# LAYOUT
# =========================================================

left, right = st.columns([3,1])

logs = []
hits = []

with left:

    st.markdown("""
    <div class="glass">
        <div class="section-title">
            Live Console
        </div>
    """, unsafe_allow_html=True)

    console_placeholder = st.empty()

    st.markdown("</div>", unsafe_allow_html=True)

with right:

    st.markdown("""
    <div class="glass">
        <div class="section-title">
            Statistics
        </div>
    """, unsafe_allow_html=True)

    metric_placeholder = st.empty()

    metric_placeholder.metric(
        "Hits Found",
        0
    )

    st.markdown("<br>", unsafe_allow_html=True)

    start = st.button("Start Audit")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# FUNCTIONS
# =========================================================

def render_logs():

    content = "<br>".join(logs[-120:])

    console_placeholder.markdown(
        f'''
        <div class="console">
        {content}
        </div>
        ''',
        unsafe_allow_html=True
    )

def log_callback(msg):

    logs.append(msg)

    render_logs()

def hit_callback(hit):

    hits.append(hit)

    metric_placeholder.metric(
        "Hits Found",
        len(hits)
    )

    logs.append(f"""
    ✅ SUCCESS<br>
    Host : {hit['host']}<br>
    Port : {hit['port']}<br>
    Email : {hit['email']}<br>
    Pass : {hit['password']}<br>
    ─────────────────────
    """)

    render_logs()

# =========================================================
# START
# =========================================================

if start:

    if not uploaded_file:

        st.warning("Please upload combo file")

    else:

        try:

            combos_by_domain = load_combos_by_domain(
                "temp_combo.txt"
            )

            logs.append(
                f"Loaded {len(combos_by_domain)} domains"
            )

            render_logs()

            for domain, combos in combos_by_domain.items():

                logs.append(
                    f"Scanning : {domain}"
                )

                render_logs()

                bruteforce_domain(
                    domain=domain,
                    combos=combos,
                    log_callback=log_callback,
                    hit_callback=hit_callback
                )

            st.success("Audit completed")

        except Exception as e:

            st.error(str(e))

# =========================================================
# RESULTS
# =========================================================

if hits:

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-subtitle">
    Results
    </div>
    """, unsafe_allow_html=True)

    for hit in hits:

        st.markdown(
            f"""
            <div class="hit-card">

            <b>Host :</b> {hit['host']}<br>
            <b>Port :</b> {hit['port']}<br>
            <b>Email :</b> {hit['email']}<br>
            <b>Password :</b> {hit['password']}

            </div>
            """,
            unsafe_allow_html=True
        )
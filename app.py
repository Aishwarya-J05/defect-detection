import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(
    page_title="SteelSense AI — Defect Detection",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #08080f !important;
    color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 40% at 50% -10%, rgba(255,107,43,0.12) 0%, transparent 60%),
        #08080f !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── LANDING ── */
.landing {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.landing::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,107,43,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,107,43,0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,107,43,0.1);
    border: 1px solid rgba(255,107,43,0.35);
    color: #ff6b2b;
    padding: 8px 20px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 32px;
    font-family: 'JetBrains Mono', monospace;
    animation: fadeUp 0.6s ease both;
}

.hero-title {
    font-size: clamp(2.8rem, 7vw, 5.5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -2px;
    margin-bottom: 24px;
    animation: fadeUp 0.6s 0.1s ease both;
}

.hero-title span { color: #ff6b2b; }

.hero-sub {
    font-size: 1.1rem;
    color: #64748b;
    max-width: 520px;
    line-height: 1.7;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    margin-bottom: 48px;
    animation: fadeUp 0.6s 0.2s ease both;
}

.stats-row {
    display: flex;
    gap: 0;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 48px;
    animation: fadeUp 0.6s 0.3s ease both;
}

.stat-box {
    padding: 24px 40px;
    background: #12121a;
    border-right: 1px solid #1e1e2e;
    text-align: center;
}
.stat-box:last-child { border-right: none; }
.stat-val { font-size: 2rem; font-weight: 800; color: #ff6b2b; }
.stat-label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; font-family: 'JetBrains Mono', monospace; }

.features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    max-width: 860px;
    width: 100%;
    margin-bottom: 56px;
    animation: fadeUp 0.6s 0.4s ease both;
}

.feature-card {
    background: #12121a;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    padding: 28px 24px;
    text-align: left;
    transition: border-color 0.2s, transform 0.2s;
}
.feature-card:hover { border-color: rgba(255,107,43,0.4); transform: translateY(-4px); }
.feature-icon { font-size: 2rem; margin-bottom: 12px; }
.feature-title { font-size: 15px; font-weight: 700; margin-bottom: 8px; }
.feature-desc { font-size: 12px; color: #64748b; line-height: 1.6; font-family: 'JetBrains Mono', monospace; }

.tech-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 56px;
    animation: fadeUp 0.6s 0.5s ease both;
}

.tech-pill {
    padding: 8px 18px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid;
}
.pill-orange { background: rgba(255,107,43,0.1); border-color: rgba(255,107,43,0.3); color: #ff6b2b; }
.pill-green  { background: rgba(34,197,94,0.1);  border-color: rgba(34,197,94,0.3);  color: #22c55e; }
.pill-purple { background: rgba(124,58,237,0.1); border-color: rgba(124,58,237,0.3); color: #a78bfa; }
.pill-yellow { background: rgba(234,179,8,0.1);  border-color: rgba(234,179,8,0.3);  color: #eab308; }

/* ── APP HEADER ── */
.app-header {
    background: #0d0d14;
    border-bottom: 1px solid #1e1e2e;
    padding: 16px 40px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.app-logo { font-size: 22px; font-weight: 800; }
.app-logo span { color: #ff6b2b; }
.app-tag { font-size: 10px; font-family: 'JetBrains Mono', monospace; color: #64748b; background: #1e1e2e; padding: 3px 10px; border-radius: 100px; letter-spacing: 1px; }

/* ── UPLOAD ZONE ── */
.upload-section {
    padding: 40px;
    max-width: 1100px;
    margin: 0 auto;
}
.section-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #ff6b2b;
    font-weight: 700;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: #1e1e2e; }

/* ── SEVERITY BADGES ── */
.sev-HIGH   { background: rgba(239,68,68,0.15);  border: 1px solid rgba(239,68,68,0.4);  color: #f87171; padding: 4px 14px; border-radius: 100px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.sev-MEDIUM { background: rgba(234,179,8,0.15);  border: 1px solid rgba(234,179,8,0.4);  color: #eab308; padding: 4px 14px; border-radius: 100px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.sev-LOW    { background: rgba(34,197,94,0.15);  border: 1px solid rgba(34,197,94,0.4);  color: #22c55e; padding: 4px 14px; border-radius: 100px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

.defect-card {
    background: #12121a;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}
.defect-card:hover { border-color: rgba(255,107,43,0.3); }
.defect-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.defect-name { font-size: 16px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.defect-conf { font-size: 12px; color: #64748b; font-family: 'JetBrains Mono', monospace; }
.info-block { background: #0d0d14; border-radius: 10px; padding: 14px 18px; margin-top: 10px; }
.info-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #ff6b2b; font-weight: 700; margin-bottom: 6px; font-family: 'JetBrains Mono', monospace; }
.info-text { font-size: 13px; color: #94a3b8; line-height: 1.6; font-family: 'JetBrains Mono', monospace; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"

# ══════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
    <div class="landing">
        <div style="position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;">
            <div class="badge">⚙ AI-Powered · Real-Time · Industrial Grade</div>
            <h1 class="hero-title">Steel<span>Sense</span> AI</h1>
            <p class="hero-sub">
                Upload any steel surface image and get instant defect detection powered by
                YOLOv8 computer vision + Gemini AI explanation engine.
            </p>
            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-val">6</div>
                    <div class="stat-label">Defect Types</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">73.6%</div>
                    <div class="stat-label">mAP50 Score</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">&lt;2s</div>
                    <div class="stat-label">Analysis Time</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">1800</div>
                    <div class="stat-label">Training Images</div>
                </div>
            </div>
            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-title">Precision Detection</div>
                    <div class="feature-desc">YOLOv8 model trained on NEU Steel dataset detects crazing, inclusion, patches, pitting, rolled-in scale and scratches.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-title">GenAI Explanation</div>
                    <div class="feature-desc">Gemini Vision API analyzes each defect crop and generates plain-English cause analysis and recommended actions.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">Instant Reports</div>
                    <div class="feature-desc">Get severity-coded inspection reports with annotated images in under 2 seconds. Ready for real industrial use.</div>
                </div>
            </div>
            <div class="tech-row">
                <span class="tech-pill pill-orange">YOLOv8</span>
                <span class="tech-pill pill-purple">Gemini Vision</span>
                <span class="tech-pill pill-green">FastAPI</span>
                <span class="tech-pill pill-yellow">Streamlit</span>
                <span class="tech-pill pill-orange">OpenCV</span>
                <span class="tech-pill pill-purple">Python</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 Launch Inspector", use_container_width=True, type="primary"):
            st.session_state.page = "app"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# APP PAGE
# ══════════════════════════════════════════════════════════════════════════
else:
    # Header
    st.markdown("""
    <div class="app-header">
        <div class="app-logo">Steel<span>Sense</span> AI</div>
        <div class="app-tag">DEFECT INSPECTOR v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="upload-section">', unsafe_allow_html=True)

    # Back button
    if st.button("← Back to Home"):
        st.session_state.page = "landing"
        st.rerun()

    st.markdown('<div class="section-label">Upload Image</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload a steel surface image",
        type=['jpg', 'jpeg', 'png'],
        label_visibility="collapsed"
    )

    if uploaded:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-label">Original Image</div>', unsafe_allow_html=True)
            st.image(uploaded, use_container_width=True)

        with st.spinner("⚙️ Running defect detection + AI analysis..."):
            try:
                response = requests.post(
                    "http://localhost:8000/analyze",
                    files={"file": (uploaded.name, uploaded.getvalue(), "image/jpeg")}
                ).json()

                with col2:
                    st.markdown('<div class="section-label">Detected Defects</div>', unsafe_allow_html=True)
                    img_bytes = base64.b64decode(response["annotated_image"])
                    img = Image.open(io.BytesIO(img_bytes))
                    st.image(img, use_container_width=True)

                st.markdown(f'<div class="section-label">Analysis Report — {len(response["detections"])} defect(s) found</div>', unsafe_allow_html=True)

                if len(response["detections"]) == 0:
                    st.success("✅ No defects detected — surface appears clean!")
                else:
                    for i, det in enumerate(response["detections"]):
                        sev = det["severity"]
                        st.markdown(f"""
                        <div class="defect-card">
                            <div class="defect-header">
                                <div class="defect-name">⚠ Defect {i+1} — {det['defect_type']}</div>
                                <div style="display:flex;align-items:center;gap:12px;">
                                    <span class="defect-conf">{det['confidence']:.0%} confidence</span>
                                    <span class="sev-{sev}">{sev}</span>
                                </div>
                            </div>
                            <div class="info-block">
                                <div class="info-label">Explanation</div>
                                <div class="info-text">{det['explanation']}</div>
                            </div>
                            <div class="info-block">
                                <div class="info-label">Probable Cause</div>
                                <div class="info-text">{det['probable_cause']}</div>
                            </div>
                            <div class="info-block">
                                <div class="info-label">Recommended Action</div>
                                <div class="info-text">{det['recommended_action']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error connecting to backend: {str(e)}")
                st.info("Make sure the FastAPI backend is running: `uvicorn api:app --reload`")

    st.markdown('</div>', unsafe_allow_html=True)
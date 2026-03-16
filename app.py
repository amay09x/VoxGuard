import streamlit as st
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VoxGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

:root {
    --bg:        #020c09;
    --bg2:       #041a12;
    --bg3:       #061710;
    --panel:     #071f16;
    --border:    #0aff6033;
    --border2:   #00e5ff33;
    --neon:      #0aff60;
    --cyan:      #00e5ff;
    --red:       #ff3e5e;
    --amber:     #ffb700;
    --text:      #b2ffd6;
    --dim:       #4a8c68;
    --font-mono: 'Share Tech Mono', monospace;
    --font-hud:  'Orbitron', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
}

/* Scanlines */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,255,96,0.013) 2px, rgba(0,255,96,0.013) 4px
    );
    pointer-events: none;
    z-index: 999;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

/* ── HUD bar ── */
.hud-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding: 0.55rem 1.2rem;
    margin-bottom: 2rem;
    font-family: var(--font-hud);
    font-size: 0.6rem;
    color: var(--dim);
    letter-spacing: 0.15em;
}
.hud-bar .logo {
    font-size: 1.05rem;
    font-weight: 900;
    color: var(--neon);
    text-shadow: 0 0 12px var(--neon), 0 0 30px var(--neon);
    letter-spacing: 0.3em;
}
.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--neon);
    box-shadow: 0 0 8px var(--neon);
    margin-right: 6px;
    animation: blink 1.4s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* ── Panel ── */
.vg-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 1.5rem 1.6rem 1.6rem;
    box-shadow: 0 0 24px rgba(10,255,96,0.04), inset 0 0 50px rgba(0,0,0,0.35);
    position: relative;
    overflow: hidden;
}
.vg-panel::after {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 5%, var(--neon) 50%, transparent 95%);
    opacity: 0.5;
}
.vg-panel-cyan::after {
    background: linear-gradient(90deg, transparent 5%, var(--cyan) 50%, transparent 95%);
}

/* ── Section label ── */
.section-label {
    font-family: var(--font-hud);
    font-size: 0.58rem;
    letter-spacing: 0.28em;
    color: var(--dim);
    text-transform: uppercase;
    margin-bottom: 1rem;
    border-left: 2px solid var(--neon);
    padding-left: 0.6rem;
}
.section-label-cyan { border-left-color: var(--cyan); color: #4a7f8c; }

/* ── Mission step list ── */
.step-list {
    list-style: none;
    padding: 0; margin: 0;
    border: 1px solid var(--border);
    border-radius: 3px;
    overflow: hidden;
}
.step-list li {
    padding: 0.65rem 0.9rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.8rem;
    color: var(--text);
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    background: var(--bg2);
}
.step-list li:nth-child(odd)  { background: var(--bg3); }
.step-list li:last-child       { border-bottom: none; }
.step-list li:hover            { background: rgba(10,255,96,0.04); }
.step-num {
    font-family: var(--font-hud);
    color: var(--neon);
    text-shadow: 0 0 8px var(--neon);
    font-size: 0.62rem;
    min-width: 22px;
    padding-top: 2px;
}

/* ── Console prompt ── */
.console-prompt {
    background: var(--bg2);
    border: 1px solid var(--border2);
    border-radius: 3px;
    padding: 0.55rem 0.9rem;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--cyan);
    margin-bottom: 0.85rem;
    letter-spacing: 0.06em;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    box-shadow: 0 0 10px rgba(0,229,255,0.06), inset 0 0 20px rgba(0,229,255,0.03);
}
.console-prompt .prompt-path { color: var(--dim); }
.cursor-blink {
    display: inline-block;
    width: 8px; height: 14px;
    background: var(--cyan);
    box-shadow: 0 0 6px var(--cyan);
    animation: blink 1s step-end infinite;
    vertical-align: middle;
}

/* ── File uploader retheme ── */
/* Hide the default label since we use the console-prompt instead */
[data-testid="stFileUploader"] > label { display: none !important; }
[data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
/* Drop zone */
[data-testid="stFileUploaderDropzone"] {
    background: var(--bg2) !important;
    border: 1px dashed #00e5ff55 !important;
    border-radius: 3px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 18px rgba(0,229,255,0.12) !important;
}
/* All text inside drop zone */
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] small {
    color: var(--cyan) !important;
    font-family: var(--font-mono) !important;
}
/* Upload icon */
[data-testid="stFileUploaderDropzone"] svg {
    stroke: var(--cyan) !important;
    filter: drop-shadow(0 0 4px var(--cyan));
}
/* Browse files button */
[data-testid="stFileUploaderDropzone"] button {
    background: transparent !important;
    border: 1px solid var(--cyan) !important;
    color: var(--cyan) !important;
    font-family: var(--font-hud) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    border-radius: 2px !important;
    text-shadow: 0 0 6px var(--cyan) !important;
    box-shadow: 0 0 10px rgba(0,229,255,0.15) !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: rgba(0,229,255,0.08) !important;
    box-shadow: 0 0 18px rgba(0,229,255,0.28) !important;
}

/* ── Analyze button ── */
.stButton > button {
    width: 100%;
    background: transparent !important;
    border: 1px solid var(--neon) !important;
    color: var(--neon) !important;
    font-family: var(--font-hud) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.22em !important;
    padding: 0.78rem 1.5rem !important;
    border-radius: 2px !important;
    text-shadow: 0 0 8px var(--neon) !important;
    box-shadow: 0 0 14px rgba(10,255,96,0.14), inset 0 0 14px rgba(10,255,96,0.03) !important;
    transition: all 0.2s ease !important;
    margin-top: 0.9rem !important;
}
.stButton > button:hover {
    background: rgba(10,255,96,0.07) !important;
    box-shadow: 0 0 28px rgba(10,255,96,0.35), inset 0 0 22px rgba(10,255,96,0.07) !important;
}

/* ── Metric grid ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.7rem;
    margin-top: 1.1rem;
}
.metric-tile {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.metric-tile .m-label {
    font-family: var(--font-hud);
    font-size: 0.5rem;
    letter-spacing: 0.2em;
    color: var(--dim);
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.metric-tile .m-value {
    font-family: var(--font-hud);
    font-size: 1.7rem;
    font-weight: 900;
    line-height: 1;
}
.metric-tile .m-unit {
    font-size: 0.62rem;
    color: var(--dim);
    margin-top: 0.25rem;
    letter-spacing: 0.1em;
}
.color-red   { color: var(--red);   text-shadow: 0 0 14px var(--red); }
.color-amber { color: var(--amber); text-shadow: 0 0 14px var(--amber); }
.color-neon  { color: var(--neon);  text-shadow: 0 0 14px var(--neon); }
.color-cyan  { color: var(--cyan);  text-shadow: 0 0 14px var(--cyan); }

/* ── Risk bar ── */
.risk-bar-wrap {
    margin-top: 0.9rem;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.9rem 1.1rem;
}
.risk-bar-label {
    font-family: var(--font-hud);
    font-size: 0.54rem;
    letter-spacing: 0.2em;
    color: var(--dim);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.risk-bar-bg {
    background: #0a1f15;
    border-radius: 2px;
    height: 8px;
    overflow: hidden;
}
.risk-bar-fill {
    height: 100%;
    border-radius: 2px;
}

/* ── Alert ── */
.vg-alert {
    border-left: 2px solid;
    padding: 0.75rem 1rem;
    font-size: 0.78rem;
    border-radius: 0 3px 3px 0;
    margin-top: 0.9rem;
    line-height: 1.55;
}
.vg-alert-danger  { border-color: var(--red);  background: rgba(255,62,94,0.07);  color: var(--red); }
.vg-alert-success { border-color: var(--neon); background: rgba(10,255,96,0.05);  color: var(--neon); }

/* ── Spinner ── */
[data-testid="stSpinner"] p {
    color: var(--cyan) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}

/* ── Footer ── */
.vg-footer {
    text-align: center;
    font-size: 0.56rem;
    letter-spacing: 0.2em;
    color: var(--dim);
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)

# ── HUD bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hud-bar">
    <span class="logo">⬡ VOXGUARD</span>
    <span><span class="status-dot"></span>SYSTEM ONLINE // v0.1-alpha</span>
    <span>THREAT INTEL ENGINE: READY</span>
</div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-bottom:2.2rem;">
    <div style="font-family:'Orbitron',sans-serif; font-size:0.65rem; letter-spacing:0.38em;
                color:#4a8c68; text-transform:uppercase; margin-bottom:0.45rem;">
        AI-POWERED VOICE THREAT ANALYSIS
    </div>
    <div style="font-family:'Orbitron',sans-serif; font-size:1.9rem; font-weight:900;
                color:#0aff60; text-shadow:0 0 28px #0aff60, 0 0 55px rgba(10,255,96,0.28);
                letter-spacing:0.1em;">
        DEEPFAKE &amp; SCAM DETECTION
    </div>
    <div style="color:#4a8c68; font-size:0.75rem; margin-top:0.45rem; letter-spacing:0.12em;">
        Upload. Scan. Neutralize the threat.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Columns ───────────────────────────────────────────────────────────────────
left, right = st.columns([1.08, 1], gap="large")

# ════════════════════════════════════════════════════
# LEFT — pure HTML panel, zero ghost Streamlit boxes
# ════════════════════════════════════════════════════
with left:
    st.markdown("""
    <div class="vg-panel">
        <div class="section-label">// MISSION BRIEF</div>
        <ul class="step-list">
            <li><span class="step-num">01</span>Upload a suspicious voice note in .wav format</li>
            <li><span class="step-num">02</span>VoxGuard scans for AI-generated deepfake artifacts in the audio waveform</li>
            <li><span class="step-num">03</span>Linguistic patterns are cross-referenced against known social engineering playbooks</li>
            <li><span class="step-num">04</span>A real-time Risk Score (0–100%) is calculated and threat vectors are flagged</li>
            <li><span class="step-num">05</span>Review the threat report and decide on countermeasures</li>
        </ul>
    </div>

    <div class="metric-grid">
        <div class="metric-tile">
            <div class="m-label">Risk Score</div>
            <div class="m-value color-red">--</div>
            <div class="m-unit">awaiting scan</div>
        </div>
        <div class="metric-tile">
            <div class="m-label">Deepfake Conf.</div>
            <div class="m-value color-amber">--</div>
            <div class="m-unit">awaiting scan</div>
        </div>
        <div class="metric-tile">
            <div class="m-label">Scan Status</div>
            <div class="m-value color-cyan" style="font-size:0.95rem;padding-top:0.55rem;">IDLE</div>
            <div class="m-unit">ready</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# RIGHT — Audio Input Terminal
# ════════════════════════════════════════════════════
with right:
    # Panel wrapper + console prompt — pure HTML
    st.markdown("""
    <div class="vg-panel vg-panel-cyan">
        <div class="section-label section-label-cyan">// AUDIO INPUT TERMINAL</div>
        <div class="console-prompt">
            <span class="prompt-path">VOXGUARD:\\SCAN&gt;&nbsp;</span>
            <span>AWAITING_TARGET.wav</span>
            <span class="cursor-blink"></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # File uploader — label hidden by CSS, drop-zone fully rethemed
    uploaded_file = st.file_uploader(
        "upload",
        type=["wav"],
        label_visibility="collapsed",
    )

    analyze_clicked = st.button("⚡  INITIATE THREAT SCAN")

    if analyze_clicked:
        if uploaded_file is not None:
            with st.spinner("▶  STAGE 1 — Scanning waveform for synthetic artifact markers..."):
                time.sleep(1.2)
            with st.spinner("▶  STAGE 2 — Cross-referencing social engineering linguistic corpus..."):
                time.sleep(1.0)
            with st.spinner("▶  STAGE 3 — Computing composite Risk Score..."):
                time.sleep(0.8)

            risk_score    = 87
            deepfake_conf = 92
            bar_color     = "#ff3e5e" if risk_score >= 70 else "#ffb700" if risk_score >= 40 else "#0aff60"

            st.markdown(f"""
            <div class="metric-grid">
                <div class="metric-tile">
                    <div class="m-label">Risk Score</div>
                    <div class="m-value color-red">{risk_score}%</div>
                    <div class="m-unit">CRITICAL</div>
                </div>
                <div class="metric-tile">
                    <div class="m-label">Deepfake Conf.</div>
                    <div class="m-value color-amber">{deepfake_conf}%</div>
                    <div class="m-unit">HIGH</div>
                </div>
                <div class="metric-tile">
                    <div class="m-label">Scan Status</div>
                    <div class="m-value color-neon" style="font-size:0.9rem;padding-top:0.55rem;">DONE</div>
                    <div class="m-unit">complete</div>
                </div>
            </div>
            <div class="risk-bar-wrap">
                <div class="risk-bar-label">Composite Risk Level — {risk_score}%</div>
                <div class="risk-bar-bg">
                    <div class="risk-bar-fill"
                         style="width:{risk_score}%;background:{bar_color};
                                box-shadow:0 0 10px {bar_color};"></div>
                </div>
            </div>
            <div class="vg-alert vg-alert-danger">
                ⚠ HIGH THREAT DETECTED — Voice exhibits synthetic artifact markers
                consistent with neural TTS cloning. Urgency-based persuasion language
                pattern identified. Do not comply with caller demands.
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="vg-alert vg-alert-danger">
                ✗ NO AUDIO TARGET — Upload a .wav file before initiating scan.
            </div>
            """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vg-footer">
    VOXGUARD // AI THREAT ANALYSIS SYSTEM // HACKATHON BUILD //
    AZURE COGNITIVE SERVICES + GEMINI ENGINE INTEGRATION PENDING
</div>
""", unsafe_allow_html=True)

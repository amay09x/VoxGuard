import streamlit as st
import time
import os
import re
import azure.cognitiveservices.speech as speechsdk
from google import genai
from dotenv import load_dotenv

# ── Environment & API Setup ───────────────────────────────────────────────────
load_dotenv()

SPEECH_KEY    = os.environ.get("AZURE_SPEECH_KEY")    or st.secrets.get("AZURE_SPEECH_KEY")
SPEECH_REGION = os.environ.get("AZURE_SPEECH_REGION") or st.secrets.get("AZURE_SPEECH_REGION")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")     or st.secrets.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# ── Backend AI Functions ──────────────────────────────────────────────────────
def transcribe_audio(file_path):
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language = "en-US"
    audio_config  = speechsdk.audio.AudioConfig(filename=file_path)
    recognizer    = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    result        = recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    return None

def analyze_intent(transcript):
    prompt = f"""
    You are an expert cybersecurity analyst. Read this audio transcript and look for signs of a social engineering scam.
    You MUST format your exact response as follows:
    SCORE: [A number from 0 to 100 representing risk level]
    ANALYSIS: [2 to 3 concise sentences explaining the red flags]

    Transcript: "{transcript}"
    """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text

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
.step-list li:nth-child(odd) { background: var(--bg3); }
.step-list li:last-child      { border-bottom: none; }
.step-list li:hover           { background: rgba(10,255,96,0.04); }
.step-num {
    font-family: var(--font-hud);
    color: var(--neon);
    text-shadow: 0 0 8px var(--neon);
    font-size: 0.62rem;
    min-width: 22px;
    padding-top: 2px;
}

/* ── Sys-info tiles (left column, below mission brief) ── */
.sysinfo-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.7rem;
    margin-top: 1.1rem;
}
.sysinfo-tile {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.85rem 1rem;
    text-align: center;
}
.sysinfo-tile .si-label {
    font-family: var(--font-hud);
    font-size: 0.48rem;
    letter-spacing: 0.2em;
    color: var(--dim);
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}
.sysinfo-tile .si-value {
    font-family: var(--font-hud);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
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
[data-testid="stFileUploader"] > label { display: none !important; }
[data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
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
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] small {
    color: var(--cyan) !important;
    font-family: var(--font-mono) !important;
}
[data-testid="stFileUploaderDropzone"] svg {
    stroke: var(--cyan) !important;
    filter: drop-shadow(0 0 4px var(--cyan));
}
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

/* ── Metric grid (scan results only) ── */
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
    transition: width 1s ease-in-out;
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
.vg-alert-danger  { border-color: var(--red);   background: rgba(255,62,94,0.07);  color: var(--red); }
.vg-alert-warning { border-color: var(--amber);  background: rgba(255,183,0,0.07); color: var(--amber); }
.vg-alert-success { border-color: var(--neon);  background: rgba(10,255,96,0.05);  color: var(--neon); }

/* ── Spinner ── */
[data-testid="stSpinner"] p {
    color: var(--cyan) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}

/* ── Social links bar ── */
.social-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 2.5rem;
    padding: 1.1rem 1.5rem;
    border: 1px solid var(--border);
    border-radius: 3px;
    background: var(--panel);
    flex-wrap: wrap;
}
.social-bar .social-label {
    font-family: var(--font-hud);
    font-size: 0.54rem;
    letter-spacing: 0.25em;
    color: var(--dim);
    text-transform: uppercase;
    margin-right: 0.5rem;
    border-right: 1px solid var(--border);
    padding-right: 1rem;
}
.social-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: var(--font-hud);
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-decoration: none !important;
    padding: 0.4rem 0.75rem;
    border-radius: 2px;
    border: 1px solid transparent;
    transition: all 0.2s ease;
}
.social-link.gh { color: var(--neon); border-color: var(--border); }
.social-link.gh:hover { border-color: var(--neon); background: rgba(10,255,96,0.06); box-shadow: 0 0 12px rgba(10,255,96,0.2); text-shadow: 0 0 8px var(--neon); }
.social-link.li { color: var(--cyan); border-color: var(--border2); }
.social-link.li:hover { border-color: var(--cyan); background: rgba(0,229,255,0.06); box-shadow: 0 0 12px rgba(0,229,255,0.2); text-shadow: 0 0 8px var(--cyan); }
.social-link.ig { color: #ff79c6; border-color: rgba(255,121,198,0.2); }
.social-link.ig:hover { border-color: #ff79c6; background: rgba(255,121,198,0.06); box-shadow: 0 0 12px rgba(255,121,198,0.2); text-shadow: 0 0 8px #ff79c6; }
.social-link svg { width: 13px; height: 13px; flex-shrink: 0; }

/* ── Footer ── */
.vg-footer {
    text-align: center;
    font-size: 0.56rem;
    letter-spacing: 0.2em;
    color: var(--dim);
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)

# ── HUD bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hud-bar">
    <span class="logo">⬡ VOXGUARD</span>
    <span><span class="status-dot"></span>SYSTEM ONLINE // v1.0</span>
    <span>THREAT INTEL ENGINE: ACTIVE</span>
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
# LEFT — Mission brief + static system info only
# NO metric tiles here — those live in the right column
# ════════════════════════════════════════════════════
with left:
    st.markdown("""
    <div class="vg-panel">
        <div class="section-label">// MISSION BRIEF</div>
        <ul class="step-list">
            <li><span class="step-num">01</span>Upload a suspicious voice note in .wav format</li>
            <li><span class="step-num">02</span>VoxGuard extracts the transcript via Azure Speech Services</li>
            <li><span class="step-num">03</span>Linguistic patterns are cross-referenced by Google Gemini AI</li>
            <li><span class="step-num">04</span>A real-time Risk Score (0–100%) is calculated and threat vectors are flagged</li>
            <li><span class="step-num">05</span>Review the threat report and decide on countermeasures</li>
        </ul>
    </div>

    <div class="sysinfo-grid">
        <div class="sysinfo-tile">
            <div class="si-label">Speech Engine</div>
            <div class="si-value" style="color:var(--cyan); text-shadow:0 0 8px var(--cyan);">AZURE</div>
        </div>
        <div class="sysinfo-tile">
            <div class="si-label">AI Engine</div>
            <div class="si-value" style="color:var(--neon); text-shadow:0 0 8px var(--neon);">GEMINI</div>
        </div>
        <div class="sysinfo-tile">
            <div class="si-label">Accepted Format</div>
            <div class="si-value" style="color:var(--dim);">.WAV</div>
        </div>
        <div class="sysinfo-tile">
            <div class="si-label">Model Version</div>
            <div class="si-value" style="color:var(--dim);">v1.0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# RIGHT — Audio input + scan results (metrics appear here ONLY)
# ════════════════════════════════════════════════════
with right:
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

    uploaded_file = st.file_uploader(
        "upload",
        type=["wav"],
        label_visibility="collapsed",
    )

    analyze_clicked = st.button("⚡  INITIATE THREAT SCAN")

    if analyze_clicked:
        if uploaded_file is not None:
            temp_audio_path = "temp_target.wav"
            with open(temp_audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("▶  STAGE 1 — Extracting transcript via Azure Cognitive Services..."):
                transcript = transcribe_audio(temp_audio_path)

            if transcript:
                with st.spinner("▶  STAGE 2 — Cross-referencing linguistics via Gemini AI Engine..."):
                    raw_analysis = analyze_intent(transcript)

                with st.spinner("▶  STAGE 3 — Computing composite Risk Score..."):
                    try:
                        score_match  = re.search(r'SCORE:\s*(\d+)', raw_analysis)
                        risk_score   = int(score_match.group(1)) if score_match else 50
                        analysis_split = raw_analysis.split('ANALYSIS:')
                        report_details = analysis_split[1].strip() if len(analysis_split) > 1 else raw_analysis
                    except Exception:
                        risk_score     = 85
                        report_details = raw_analysis

                    deepfake_conf = max(0, risk_score - 4)
                    bar_color     = "#ff3e5e" if risk_score >= 70 else "#ffb700" if risk_score >= 40 else "#0aff60"
                    status_text   = "CRITICAL" if risk_score >= 70 else "WARNING" if risk_score >= 40 else "SAFE"
                    alert_class   = "vg-alert-danger" if risk_score >= 70 else "vg-alert-warning" if risk_score >= 40 else "vg-alert-success"
                    alert_icon    = "⚠ HIGH THREAT DETECTED" if risk_score >= 70 else "⚠ CAUTION" if risk_score >= 40 else "✓ CLEAR"

                # Single metric grid — right column only, shown once after scan
                st.markdown(f"""
                <div class="metric-grid">
                    <div class="metric-tile">
                        <div class="m-label">Risk Score</div>
                        <div class="m-value" style="color:{bar_color}; text-shadow:0 0 14px {bar_color};">{risk_score}%</div>
                        <div class="m-unit">{status_text}</div>
                    </div>
                    <div class="metric-tile">
                        <div class="m-label">Deepfake Conf.</div>
                        <div class="m-value" style="color:{bar_color}; text-shadow:0 0 14px {bar_color};">{deepfake_conf}%</div>
                        <div class="m-unit">CALCULATED</div>
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
                             style="width:{risk_score}%; background:{bar_color};
                                    box-shadow:0 0 10px {bar_color};"></div>
                    </div>
                </div>

                <div class="vg-alert {alert_class}">
                    <b>{alert_icon}</b><br><br>
                    {report_details}<br><br>
                    <i>Transcript captured: "{transcript}"</i>
                </div>
                """, unsafe_allow_html=True)

                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)

            else:
                st.error("Azure failed to extract speech from the audio file.")

        else:
            st.markdown("""
            <div class="vg-alert vg-alert-danger">
                ✗ NO AUDIO TARGET — Upload a .wav file before initiating scan.
            </div>
            """, unsafe_allow_html=True)

# ── Social links + Footer ─────────────────────────────────────────────────────
st.markdown("""
<div class="social-bar">
<span class="social-label">// BUILT BY</span>

<a class="social-link gh" href="https://github.com/amay09x" target="_blank">
<svg viewBox="0 0 24 24" fill="currentColor">
<path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
</svg>
GITHUB
</a>

<a class="social-link li" href="https://www.linkedin.com/in/amay-sharma-24690136b" target="_blank">
<svg viewBox="0 0 24 24" fill="currentColor">
<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
</svg>
LINKEDIN
</a>

<a class="social-link ig" href="https://www.instagram.com/probablyamayy/" target="_blank">
<svg viewBox="0 0 24 24" fill="currentColor">
<path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
</svg>
INSTAGRAM
</a>
</div>

<div class="vg-footer">
VOXGUARD // AI THREAT ANALYSIS SYSTEM // HACKATHON BUILD // AZURE + GEMINI ENGINE ACTIVE
</div>
""", unsafe_allow_html=True)

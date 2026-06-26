# ============================================================
# frontend.py
# Aplikasi Streamlit — Platform Konsultasi Bisnis
# Solusi Mitra UMKM — Desain Profesional & Elegan
# ============================================================

import os
import time
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# ─── Load Environment Variables ─────────────────────────────────────────────
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# ============================================================
# KONFIGURASI HALAMAN STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Solusi Mitra UMKM — Platform Konsultasi Bisnis",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS — Desain Profesional & Elegan
# ============================================================
def inject_custom_css():
    """Inject CSS untuk tampilan profesional, elegan, dan membangun kepercayaan."""
    st.markdown("""
    <style>
    /* ─── Import Fonts ───────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ─── Design Tokens — Selaras Logo Solusi Mitra UMKM ───────
         Logo: Gold #D4900A | Biru Elektrik #1A6FD4 | Navy Gelap
    ──────────────────────────────────────────────────────────── */
    :root {
        /* Core brand dari logo */
        --navy:          #0B1829;
        --navy-mid:      #13253F;
        --navy-light:    #1C3456;

        /* Biru elektrik (panah logo) */
        --accent:        #1A6FD4;
        --accent-dark:   #1259AD;
        --accent-glow:   rgba(26, 111, 212, 0.15);

        /* Gold amber (bar chart logo) */
        --gold:          #D4900A;
        --gold-dark:     #B07608;
        --gold-light:    #F5C842;
        --gold-bg:       #FEF8E7;
        --gold-border:   #F0D080;

        /* Surfaces */
        --surface:       #FFFFFF;
        --bg:            #F2F5FA;
        --bg-dark:       #E8EDF5;

        /* Borders */
        --border:        #D6DCE8;
        --border-subtle: #EAEef6;

        /* Text */
        --text-primary:  #0D1A2D;
        --text-secondary:#3D4F68;
        --text-muted:    #7A8AA0;

        /* Status */
        --success:        #0A6640;
        --success-bg:     #E8F7F0;
        --success-border: #A8D8C0;
        --error:          #8B1A1A;
        --error-bg:       #FBF0F0;
        --error-border:   #F0B8B8;
        --warning:        #7A4800;
        --warning-bg:     #FFF6E8;
        --warning-border: #F0D090;
    }

    /* ─── Global Reset ───────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
        background-color: var(--bg);
    }

    /* Sembunyikan elemen Streamlit default */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    /* ─── Sidebar ────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: var(--navy) !important;
        border-right: 1px solid rgba(212, 144, 10, 0.12);
    }
    section[data-testid="stSidebar"] * {
        color: #B8C8DF !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #B8C8DF !important;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.2px;
        transition: all 0.2s ease;
        padding: 0.5rem 1rem;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(26, 111, 212, 0.12) !important;
        border-color: rgba(26, 111, 212, 0.4) !important;
        color: #7ABAFF !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(212, 144, 10, 0.15) !important;
        border-color: rgba(212, 144, 10, 0.45) !important;
        color: #F5C842 !important;
    }

    /* ─── Main Content Area ──────────────────────────────────── */
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 1100px;
    }

    /* ─── Page Header ────────────────────────────────────────── */
    .page-header {
        border-bottom: 1px solid var(--border);
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }
    .page-header .eyebrow {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 0.4rem;
    }
    .page-header h2 {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.9rem;
        font-weight: 700;
        color: var(--navy);
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.3px;
        line-height: 1.2;
    }
    .page-header .subtitle {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 400;
        line-height: 1.5;
    }

    /* ─── Stat Cards ─────────────────────────────────────────── */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        position: relative;
        overflow: hidden;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px;
        height: 100%;
    }
    /* Gold untuk total — mencerminkan bar chart logo */
    .stat-card.blue::before   { background: var(--gold); }
    .stat-card.green::before  { background: var(--accent); }
    .stat-card.purple::before { background: #5C6BC0; }
    .stat-card.amber::before  { background: var(--gold-dark); }

    .stat-value {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 0.25rem;
        color: var(--navy);
    }
    .stat-card.blue   .stat-value { color: var(--gold); }
    .stat-card.green  .stat-value { color: var(--accent); }
    .stat-card.purple .stat-value { color: #5C6BC0; }
    .stat-card.amber  .stat-value { color: var(--gold-dark); }

    .stat-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ─── Form Styling ───────────────────────────────────────── */
    div[data-testid="stForm"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 2rem 2rem 1.5rem;
        box-shadow: 0 1px 4px rgba(10,22,40,0.06);
    }
    .form-section-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--text-muted);
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 0.5rem;
        margin-bottom: 0.2rem;
    }

    /* Streamlit input overrides */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-color: var(--border) !important;
        border-radius: 7px !important;
        font-size: 0.9rem !important;
        color: var(--text-primary) !important;
        background: #FAFBFD !important;
        transition: border-color 0.15s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(30, 111, 217, 0.1) !important;
        background: #FFFFFF !important;
    }
    label[data-testid="stWidgetLabel"] {
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: 0.1px !important;
    }

    /* ─── Primary Submit Button — Gold dari logo ─────────────── */
    div[data-testid="stForm"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        padding: 0.7rem 2rem !important;
        transition: opacity 0.2s ease, box-shadow 0.2s ease !important;
        box-shadow: 0 2px 12px rgba(212, 144, 10, 0.35) !important;
    }
    div[data-testid="stForm"] .stButton > button[kind="primary"]:hover {
        opacity: 0.9 !important;
        box-shadow: 0 4px 20px rgba(212, 144, 10, 0.45) !important;
    }

    /* ─── Info Box — Gold tint dari logo ────────────────────── */
    .info-box {
        background: var(--gold-bg);
        border: 1px solid var(--gold-border);
        border-left: 3px solid var(--gold);
        border-radius: 7px;
        padding: 0.9rem 1.1rem;
        color: #5C3A00;
        font-size: 0.88rem;
        line-height: 1.6;
        margin-bottom: 0.8rem;
    }

    /* ─── Consultation Cards (Dashboard) ────────────────────── */
    .consultation-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .consultation-card:hover {
        border-color: var(--gold);
        box-shadow: 0 4px 18px rgba(212, 144, 10, 0.1);
    }
    .card-business-name {
        font-size: 1rem;
        font-weight: 600;
        color: var(--navy);
        letter-spacing: -0.1px;
    }
    .card-industry {
        font-size: 0.83rem;
        color: var(--text-muted);
        margin-left: 0.4rem;
    }
    .card-preview {
        margin-top: 0.4rem;
        font-size: 0.88rem;
        color: var(--text-secondary);
        line-height: 1.55;
    }
    .card-meta {
        margin-top: 0.6rem;
        font-size: 0.78rem;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.2px;
    }

    /* ─── Status Badge ───────────────────────────────────────── */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .status-success {
        background: var(--success-bg);
        color: var(--success);
        border: 1px solid var(--success-border);
    }
    .status-failed {
        background: var(--error-bg);
        color: var(--error);
        border: 1px solid var(--error-border);
    }
    .status-pending {
        background: var(--warning-bg);
        color: var(--warning);
        border: 1px solid var(--warning-border);
    }

    /* ─── Solution Sections ──────────────────────────────────── */
    .solution-panel {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    }
    .solution-panel-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-subtle);
    }

    /* ─── Action Steps ───────────────────────────────────────── */
    .action-step {
        display: flex;
        gap: 1rem;
        padding: 1rem 1.2rem;
        background: #FAFBFD;
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        margin-bottom: 0.6rem;
        align-items: flex-start;
    }
    .step-number {
        background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 0.78rem;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .step-content { flex: 1; }
    .step-title {
        font-weight: 600;
        font-size: 0.92rem;
        color: var(--navy);
        margin-bottom: 0.3rem;
        letter-spacing: -0.1px;
    }
    .step-desc {
        color: var(--text-secondary);
        font-size: 0.875rem;
        line-height: 1.55;
    }
    .step-tags {
        margin-top: 0.55rem;
        display: flex;
        gap: 0.4rem;
        flex-wrap: wrap;
    }
    .tag {
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .tag-high     { background: var(--error-bg);   color: var(--error);   border: 1px solid var(--error-border); }
    .tag-medium   { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); }
    .tag-low      { background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); }
    .tag-timeline { background: var(--gold-bg); color: #7A4800; border: 1px solid var(--gold-border); }

    /* ─── Detail Meta Row ────────────────────────────────────── */
    .detail-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.2rem 1.6rem;
        margin-bottom: 1.5rem;
    }
    .meta-item {}
    .meta-key {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.2rem;
    }
    .meta-val {
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--navy);
    }
    .meta-val.mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: var(--accent);
    }

    /* ─── Divider ────────────────────────────────────────────── */
    .styled-divider {
        border: none;
        border-top: 1px solid var(--border-subtle);
        margin: 1.5rem 0;
    }

    /* ─── Back Button ────────────────────────────────────────── */
    .stButton > button[kind="secondary"] {
        border-color: var(--border) !important;
        color: var(--text-secondary) !important;
        border-radius: 6px !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        background: var(--surface) !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    /* ─── Section headers inside content ────────────────────── */
    .section-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.6rem;
        margin-top: 1.2rem;
    }

    /* ─── Empty State ────────────────────────────────────────── */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: var(--text-muted);
    }
    .empty-state-icon {
        width: 48px;
        height: 48px;
        border: 2px solid var(--border);
        border-radius: 50%;
        margin: 0 auto 1rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .empty-state h3 {
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        color: var(--navy);
        margin-bottom: 0.4rem;
    }
    .empty-state p {
        font-size: 0.875rem;
        color: var(--text-secondary);
    }

    /* ─── Progress bar ───────────────────────────────────────── */
    .stProgress > div > div > div > div {
        background: var(--accent) !important;
    }

    /* ─── Streamlit alerts overrides ────────────────────────── */
    .stAlert {
        border-radius: 8px !important;
        font-size: 0.88rem !important;
    }

    /* ─── Footer ─────────────────────────────────────────────── */
    .app-footer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.75rem;
        padding: 2.5rem 0 1rem 0;
        border-top: 1px solid var(--border-subtle);
        margin-top: 3rem;
        letter-spacing: 0.3px;
    }

    /* ─── Responsive: mobile ─────────────────────────────────── */
    @media (max-width: 768px) {
        .stat-grid { grid-template-columns: repeat(2, 1fr); }
        .main .block-container { padding: 1rem; }
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def check_backend_health() -> bool:
    """Cek apakah backend FastAPI sedang berjalan."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False


def call_backend_consultation(payload: dict) -> dict:
    response = requests.post(
        f"{BACKEND_URL}/api/consultations/",
        json=payload,
        timeout=120
    )
    response.raise_for_status()
    return response.json()


def fetch_consultations(page: int = 1, per_page: int = 10, status_filter: str = None) -> dict:
    params = {"page": page, "per_page": per_page}
    if status_filter and status_filter != "Semua":
        params["status"] = status_filter.lower()
    response = requests.get(f"{BACKEND_URL}/api/consultations/", params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_consultation_detail(consultation_id: int) -> dict:
    response = requests.get(f"{BACKEND_URL}/api/consultations/{consultation_id}", timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_stats() -> dict:
    try:
        response = requests.get(f"{BACKEND_URL}/api/stats/", timeout=5)
        return response.json()
    except:
        return {"total_consultations": 0, "success_count": 0, "failed_count": 0, "success_rate": 0, "avg_processing_ms": 0}


def format_datetime(iso_string: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y, %H:%M")
    except:
        return iso_string


def get_priority_tag(prioritas: str) -> str:
    p = prioritas.lower()
    if "tinggi" in p or "high" in p:
        return "tag-high"
    elif "sedang" in p or "medium" in p:
        return "tag-medium"
    return "tag-low"


# ============================================================
# KOMPONEN UI
# ============================================================

def render_page_header(eyebrow: str, title: str, subtitle: str = ""):
    """Render page header dengan tipografi hierarki yang jelas."""
    subtitle_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div class="page-header">
        <div class="eyebrow">{eyebrow}</div>
        <h2>{title}</h2>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def render_stats_cards(stats: dict):
    """Render kartu statistik dalam grid 4 kolom."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="stat-value">{stats.get('total_consultations', 0)}</div>
            <div class="stat-label">Total Konsultasi</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="stat-value">{stats.get('success_count', 0)}</div>
            <div class="stat-label">Berhasil Diproses</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="stat-value">{stats.get('success_rate', 0)}%</div>
            <div class="stat-label">Tingkat Keberhasilan</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        avg_sec = round(stats.get('avg_processing_ms', 0) / 1000, 1)
        st.markdown(f"""
        <div class="stat-card amber">
            <div class="stat-value">{avg_sec}s</div>
            <div class="stat-label">Rata-rata Waktu Analisis</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


def render_solution(ai_json: dict):
    """
    Render hasil analisis konsultasi dalam format visual profesional.
    Tanpa referensi ke terminologi 'AI' secara eksplisit.
    """
    if not ai_json:
        st.warning("Data hasil analisis tidak tersedia.")
        return

    # ─── Ringkasan Masalah ───────────────────────────────────────────────────
    st.markdown('<div class="section-label">Ringkasan Analisis Masalah</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-box">
        {ai_json.get("ringkasan_masalah", "-")}
    </div>
    """, unsafe_allow_html=True)

    # ─── Akar Masalah & Solusi Utama ────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-label">Identifikasi Akar Masalah</div>', unsafe_allow_html=True)
        st.markdown('<div class="solution-panel">', unsafe_allow_html=True)
        akar = ai_json.get("analisis_akar_masalah", [])
        for item in akar:
            st.markdown(f"— {item}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-label">Rekomendasi Solusi Utama</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="solution-panel" style="border-left: 3px solid #1E6FD9;">
            {ai_json.get("solusi_utama", "-")}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ─── Rencana Aksi ────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Rencana Tindak Lanjut</div>', unsafe_allow_html=True)
    langkah_aksi = ai_json.get("langkah_aksi", [])

    for step in langkah_aksi:
        priority_class = get_priority_tag(step.get("prioritas", ""))
        st.markdown(f"""
        <div class="action-step">
            <div class="step-number">{step.get("langkah", "?")}</div>
            <div class="step-content">
                <div class="step-title">{step.get("judul", "-")}</div>
                <div class="step-desc">{step.get("deskripsi", "-")}</div>
                <div class="step-tags">
                    <span class="tag {priority_class}">{step.get("prioritas", "-")}</span>
                    <span class="tag tag-timeline">{step.get("timeline", "-")}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ─── Dampak, Risiko, SDM, KPI ────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-label">Estimasi Dampak Bisnis</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="solution-panel">
            {ai_json.get("estimasi_dampak", "-")}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Risiko dan Mitigasi</div>', unsafe_allow_html=True)
        st.markdown('<div class="solution-panel">', unsafe_allow_html=True)
        for item in ai_json.get("risiko_dan_mitigasi", []):
            st.markdown(f"— {item}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-label">Sumber Daya yang Dibutuhkan</div>', unsafe_allow_html=True)
        st.markdown('<div class="solution-panel">', unsafe_allow_html=True)
        for item in ai_json.get("sumber_daya_dibutuhkan", []):
            st.markdown(f"— {item}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">Indikator Kinerja (KPI)</div>', unsafe_allow_html=True)
        st.markdown('<div class="solution-panel">', unsafe_allow_html=True)
        for item in ai_json.get("kpi_saran", []):
            st.markdown(f"— {item}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ─── Catatan Konsultan ───────────────────────────────────────────────────
    st.markdown('<div class="section-label">Catatan dari Tim Konsultan</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-box">
        {ai_json.get("catatan_konsultan", "-")}
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HALAMAN: KONSULTASI BARU
# ============================================================

def page_new_consultation():
    render_page_header(
        eyebrow="Layanan Konsultasi",
        title="Konsultasi Bisnis Baru",
        subtitle="Sampaikan permasalahan bisnis Anda secara lengkap untuk memperoleh analisis dan rekomendasi yang terstruktur."
    )

    with st.form("consultation_form", clear_on_submit=False):

        # ── Identitas (Opsional) ──────────────────────────────────────────────
        st.markdown('<div class="form-section-title">Data Identitas (Opsional)</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input(
                "Nama",
                placeholder="Contoh: Budi Santoso",
                help="Nama pemilik atau penanggung jawab bisnis"
            )
        with col2:
            user_email = st.text_input(
                "Alamat Email",
                placeholder="Contoh: budi@email.com",
                help="Digunakan untuk melacak riwayat konsultasi Anda"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Profil Bisnis ─────────────────────────────────────────────────────
        st.markdown('<div class="form-section-title">Profil Bisnis</div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            business_name = st.text_input(
                "Nama Bisnis *",
                placeholder="Contoh: Warung Makan Bu Sari",
                help="Nama resmi usaha atau bisnis Anda"
            )
        with col4:
            industry = st.text_input(
                "Industri / Sektor *",
                placeholder="Contoh: Kuliner & F&B, Retail Fashion, Jasa Pendidikan",
                help="Sektor industri tempat bisnis Anda beroperasi"
            )

        col5, col6 = st.columns(2)
        with col5:
            business_scale = st.selectbox(
                "Skala Bisnis *",
                options=[
                    "Mikro (kurang dari 5 karyawan)",
                    "Kecil (5 hingga 19 karyawan)",
                    "Menengah (20 hingga 99 karyawan)",
                    "Besar (100 karyawan ke atas)"
                ],
                help="Pilih skala yang paling mencerminkan kondisi bisnis Anda saat ini"
            )
        with col6:
            location = st.text_input(
                "Lokasi Operasional *",
                placeholder="Contoh: Surabaya, Jawa Timur",
                help="Kota dan provinsi tempat bisnis beroperasi"
            )

        business_description = st.text_area(
            "Deskripsi Singkat Bisnis (Opsional)",
            placeholder="Contoh: Usaha kuliner yang berdiri sejak 2015, spesialisasi masakan Padang, melayani 50–80 pelanggan per hari...",
            height=75,
            help="Konteks tambahan tentang bisnis Anda. Semakin lengkap, semakin relevan rekomendasinya."
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Deskripsi Masalah ────────────────────────────────────────────────
        st.markdown('<div class="form-section-title">Uraian Masalah Bisnis</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
            <strong>Panduan pengisian:</strong> Uraikan masalah secara spesifik — apa yang terjadi, kapan mulai terjadi, dampak yang dirasakan, dan langkah yang sudah dilakukan. Semakin rinci uraian Anda, semakin akurat rekomendasi yang akan diberikan.<br><br>
            <em>Contoh: "Omzet menurun 30% sejak tiga bulan lalu akibat masuknya kompetitor baru, sementara biaya sewa naik 20%. Sudah mencoba promosi di media sosial namun belum memberikan hasil signifikan..."</em>
        </div>
        """, unsafe_allow_html=True)

        problem_statement = st.text_area(
            "Uraian Masalah *",
            placeholder="Ceritakan permasalahan bisnis Anda secara mendetail. Apa yang terjadi? Kapan mulai? Apa yang sudah dicoba? Apa dampaknya terhadap operasional dan keuangan?",
            height=190,
            help="Minimal 20 karakter. Semakin lengkap semakin baik."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submitted = st.form_submit_button(
                "Ajukan Konsultasi",
                use_container_width=True,
                type="primary"
            )

    # ─── Proses Submit ────────────────────────────────────────────────────────
    if submitted:
        errors = []
        if not business_name.strip():
            errors.append("Nama bisnis wajib diisi.")
        if not industry.strip():
            errors.append("Industri atau sektor wajib diisi.")
        if not location.strip():
            errors.append("Lokasi operasional wajib diisi.")
        if not problem_statement.strip():
            errors.append("Uraian masalah wajib diisi.")
        elif len(problem_statement.strip()) < 20:
            errors.append("Uraian masalah minimal 20 karakter.")

        if errors:
            for err in errors:
                st.error(err)
            return

        # ─── Progress Pemrosesan ──────────────────────────────────────────────
        progress_placeholder = st.empty()
        status_placeholder   = st.empty()

        with st.spinner(""):
            progress_steps = [
                (10,  "Memvalidasi data profil bisnis..."),
                (28,  "Menganalisis skala dan sektor industri..."),
                (50,  "Menelaah dan memproses uraian masalah..."),
                (72,  "Menyusun rekomendasi dan rencana tindak lanjut..."),
                (88,  "Menyimpan hasil analisis ke basis data..."),
                (100, "Selesai."),
            ]

            progress_bar = progress_placeholder.progress(0)

            for pct, msg in progress_steps[:-2]:
                progress_bar.progress(pct)
                status_placeholder.info(msg)
                time.sleep(0.4)

            try:
                payload = {
                    "user_name":            user_name or None,
                    "user_email":           user_email or None,
                    "business_name":        business_name,
                    "industry":             industry,
                    "business_scale":       business_scale,
                    "location":             location,
                    "business_description": business_description or None,
                    "problem_statement":    problem_statement,
                }

                progress_bar.progress(72)
                status_placeholder.info("Memproses analisis mendalam... (estimasi 10–30 detik)")

                result = call_backend_consultation(payload)

                progress_bar.progress(95)
                status_placeholder.info("Menyimpan hasil ke basis data...")
                time.sleep(0.3)

                progress_bar.progress(100)
                status_placeholder.empty()
                progress_placeholder.empty()

                if result.get("success") and result.get("data"):
                    data = result["data"]
                    processing_sec = round(data.get("processing_time_ms", 0) / 1000, 1)

                    st.success(f"Analisis selesai dalam {processing_sec} detik.")

                    st.session_state["latest_consultation"] = data

                    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

                    render_page_header(
                        eyebrow="Hasil Analisis Konsultasi",
                        title=business_name,
                        subtitle=f"{industry}  •  {location}  •  {business_scale}"
                    )

                    render_solution(data.get("ai_response_json"))

                    st.markdown("<br>", unsafe_allow_html=True)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Lihat Riwayat Konsultasi", use_container_width=True):
                            st.session_state["active_page"] = "dashboard"
                            st.rerun()
                    with col_b:
                        if st.button("Ajukan Konsultasi Baru", use_container_width=True):
                            st.rerun()
                else:
                    st.error("Respons tidak valid dari server.")

            except requests.exceptions.ConnectionError:
                progress_placeholder.empty()
                status_placeholder.empty()
                st.error(f"Tidak dapat terhubung ke server backend di `{BACKEND_URL}`. Pastikan server FastAPI sudah berjalan.\n\nPerintah: `uvicorn backend:app --reload`")

            except requests.exceptions.Timeout:
                progress_placeholder.empty()
                status_placeholder.empty()
                st.error("Waktu proses habis (timeout). Server membutuhkan terlalu lama untuk merespons. Silakan coba kembali.")

            except requests.exceptions.HTTPError as e:
                progress_placeholder.empty()
                status_placeholder.empty()
                try:
                    error_detail = e.response.json().get("detail", str(e))
                except:
                    error_detail = str(e)
                st.error(f"Kesalahan dari server: {error_detail}")

            except Exception as e:
                progress_placeholder.empty()
                status_placeholder.empty()
                st.error(f"Terjadi kesalahan tidak terduga: {str(e)}")


# ============================================================
# HALAMAN: DASHBOARD RIWAYAT
# ============================================================

def page_dashboard():
    render_page_header(
        eyebrow="Riwayat Konsultasi",
        title="Dashboard Konsultasi",
        subtitle="Pantau seluruh riwayat dan status konsultasi bisnis yang telah diproses."
    )

    with st.spinner("Memuat data..."):
        stats = fetch_stats()

    render_stats_cards(stats)

    col_filter, col_refresh = st.columns([3, 1])
    with col_filter:
        status_filter = st.selectbox(
            "Filter Status",
            options=["Semua", "Success", "Failed", "Pending"],
            key="status_filter"
        )
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Perbarui Data", use_container_width=True):
            st.rerun()

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 1

    try:
        response = fetch_consultations(
            page=st.session_state["current_page"],
            per_page=8,
            status_filter=status_filter
        )

        if not response.get("success"):
            st.error("Gagal memuat riwayat konsultasi.")
            return

        data        = response["data"]
        items       = data.get("items", [])
        total       = data.get("total", 0)
        total_pages = data.get("total_pages", 1)

        if not items:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon"></div>
                <h3>Belum ada riwayat konsultasi</h3>
                <p>Mulai konsultasi pertama Anda melalui menu Konsultasi Baru di sidebar.</p>
            </div>
            """, unsafe_allow_html=True)
            return

        st.markdown(f"<p style='font-size:0.83rem; color:#8A96AA; margin-bottom:0.8rem;'>Menampilkan {len(items)} dari {total} konsultasi</p>", unsafe_allow_html=True)

        for item in items:
            status_value = item.get("status", "pending")
            status_class = f"status-{status_value}"
            status_label = {
                "success": "Selesai",
                "failed": "Gagal",
                "pending": "Diproses"
            }.get(status_value, status_value.capitalize())

            processing_sec = round(item.get("processing_time_ms", 0) / 1000, 1) if item.get("processing_time_ms") else "-"

            problem_preview = item.get("problem_statement", "")
            if len(problem_preview) > 160:
                problem_preview = problem_preview[:160] + "..."

            with st.container():
                st.markdown(f"""
                <div class="consultation-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.4rem;">
                        <div>
                            <span class="card-business-name">{item.get("business_name", "-")}</span>
                            <span class="card-industry">{item.get("industry", "-")}</span>
                        </div>
                        <div style="display:flex; gap:0.5rem; align-items:center;">
                            <span class="status-badge {status_class}">{status_label}</span>
                            <span style="font-size:0.78rem; color:#8A96AA;">{format_datetime(item.get("created_at", ""))}</span>
                        </div>
                    </div>
                    <div class="card-preview">{problem_preview}</div>
                    <div class="card-meta">
                        {item.get("location", "-")} &nbsp;&bull;&nbsp;
                        {item.get("business_scale", "-")} &nbsp;&bull;&nbsp;
                        Durasi analisis: {processing_sec}s
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_col, _ = st.columns([1, 5])
                with btn_col:
                    if st.button("Lihat Detail", key=f"detail_{item['id']}", use_container_width=True):
                        st.session_state["selected_consultation_id"] = item["id"]
                        st.session_state["active_page"] = "detail"
                        st.rerun()

        if total_pages > 1:
            st.markdown("<br>", unsafe_allow_html=True)
            cols_pg = st.columns(total_pages)
            for i in range(1, total_pages + 1):
                with cols_pg[i-1]:
                    is_current = (st.session_state["current_page"] == i)
                    if st.button(
                        str(i),
                        key=f"page_{i}",
                        use_container_width=True,
                        type="primary" if is_current else "secondary"
                    ):
                        st.session_state["current_page"] = i
                        st.rerun()

    except requests.exceptions.ConnectionError:
        st.error(f"Tidak dapat terhubung ke server backend di `{BACKEND_URL}`. Pastikan server FastAPI sudah berjalan.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")


# ============================================================
# HALAMAN: DETAIL KONSULTASI
# ============================================================

def page_consultation_detail():
    consultation_id = st.session_state.get("selected_consultation_id")
    if not consultation_id:
        st.warning("Tidak ada konsultasi yang dipilih.")
        return

    if st.button("Kembali ke Riwayat", type="secondary"):
        st.session_state["active_page"] = "dashboard"
        st.session_state.pop("selected_consultation_id", None)
        st.rerun()

    with st.spinner("Memuat detail konsultasi..."):
        try:
            response = fetch_consultation_detail(consultation_id)
        except Exception as e:
            st.error(f"Gagal memuat detail: {str(e)}")
            return

    if not response.get("success"):
        st.error("Data konsultasi tidak ditemukan.")
        return

    data    = response["data"]
    profile = data.get("business_profile", {})

    render_page_header(
        eyebrow=f"Konsultasi #{data['id']}",
        title=profile.get("business_name", "-"),
        subtitle=f"{profile.get('industry', '-')}  •  {profile.get('location', '-')}"
    )

    # ─── Meta Info ────────────────────────────────────────────────────────────
    status_val = data.get("status", "-")
    status_class = f"status-{status_val}"
    status_label = {"success": "Selesai", "failed": "Gagal", "pending": "Diproses"}.get(status_val, status_val.capitalize())

    st.markdown(f"""
    <div class="detail-meta">
        <div class="meta-item">
            <div class="meta-key">Skala Bisnis</div>
            <div class="meta-val">{profile.get("business_scale", "-")}</div>
        </div>
        <div class="meta-item">
            <div class="meta-key">Status</div>
            <div class="meta-val"><span class="status-badge {status_class}">{status_label}</span></div>
        </div>
        <div class="meta-item">
            <div class="meta-key">Durasi Analisis</div>
            <div class="meta-val mono">{round(data.get("processing_time_ms", 0)/1000, 1)}s</div>
        </div>
        <div class="meta-item">
            <div class="meta-key">Tanggal</div>
            <div class="meta-val">{format_datetime(data.get("created_at", ""))}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Masalah ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Uraian Masalah yang Dikonsultasikan</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-box">{data.get("problem_statement", "-")}</div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ─── Hasil Analisis ──────────────────────────────────────────────────────
    if data.get("status") == "success" and data.get("ai_response_json"):
        st.markdown('<div class="section-label">Hasil Analisis dan Rekomendasi</div>', unsafe_allow_html=True)
        st.caption("Data ini dimuat langsung dari basis data tanpa memproses ulang.")
        render_solution(data["ai_response_json"])

    elif data.get("status") == "failed":
        st.error(f"Konsultasi ini gagal diproses.\n\nDetail: {data.get('error_message', 'Tidak ada informasi error.')}")

    else:
        st.warning("Konsultasi masih dalam proses atau data hasil analisis belum tersedia.")


# ============================================================
# SIDEBAR NAVIGASI
# ============================================================

def render_sidebar():
    with st.sidebar:
        # ─── Branding ─────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding: 0.5rem 0 1.2rem 0;">
            <div style="font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase; color: #4A6FA5; margin-bottom: 0.3rem; font-weight: 600;">
                Platform Konsultasi
            </div>
            <div style="font-family: 'Playfair Display', serif; font-size: 1.35rem; font-weight: 700; color: #FFFFFF; line-height: 1.2; letter-spacing: -0.3px;">
                Solusi Mitra<br>UMKM
            </div>
            <div style="font-size: 0.75rem; color: #5C7BAA; margin-top: 0.4rem; font-weight: 400;">
                Didukung oleh PT HM Sampoerna Tbk.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr style="border-color: rgba(255,255,255,0.08); margin: 0 0 1rem 0;">', unsafe_allow_html=True)

        # ─── Status Backend ───────────────────────────────────────────────
        backend_ok = check_backend_health()
        status_color = "#0E6E47" if backend_ok else "#9B1C1C"
        status_bg    = "#EDFAF3" if backend_ok else "#FDF2F2"
        status_text  = "Sistem Aktif" if backend_ok else "Sistem Tidak Aktif"
        st.markdown(f"""
        <div style="background: {status_bg}; border-radius: 6px; padding: 0.55rem 0.8rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 7px; height: 7px; border-radius: 50%; background: {status_color}; flex-shrink: 0;"></div>
            <span style="font-size: 0.78rem; font-weight: 600; color: {status_color} !important;">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)

        if not backend_ok:
            st.caption(f"Server: `{BACKEND_URL}`")
            st.caption("Jalankan: `uvicorn backend:app --reload`")

        st.markdown('<hr style="border-color: rgba(255,255,255,0.08); margin: 0 0 0.8rem 0;">', unsafe_allow_html=True)

        # ─── Navigasi ────────────────────────────────────────────────────
        st.markdown("""
        <div style="font-size: 0.65rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #4A6FA5; margin-bottom: 0.5rem;">
            Navigasi
        </div>
        """, unsafe_allow_html=True)

        if "active_page" not in st.session_state:
            st.session_state["active_page"] = "new_consultation"

        if st.button(
            "Konsultasi Baru",
            use_container_width=True,
            type="primary" if st.session_state["active_page"] == "new_consultation" else "secondary"
        ):
            st.session_state["active_page"] = "new_consultation"
            st.rerun()

        if st.button(
            "Riwayat Konsultasi",
            use_container_width=True,
            type="primary" if st.session_state["active_page"] == "dashboard" else "secondary"
        ):
            st.session_state["active_page"] = "dashboard"
            st.session_state["current_page"] = 1
            st.rerun()

        st.markdown('<hr style="border-color: rgba(255,255,255,0.08); margin: 1rem 0;">', unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size: 0.72rem; color: #3D5A80; line-height: 1.6;">
            Platform konsultasi bisnis terstruktur untuk UMKM Indonesia.<br><br>
        </div>
        <div style="font-size: 0.68rem; color: #2E4166; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.2px;">
            v1.0.0 &nbsp;&bull;&nbsp; FastAPI + Streamlit
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# MAIN APP
# ============================================================

def main():
    inject_custom_css()
    render_sidebar()

    active_page = st.session_state.get("active_page", "new_consultation")

    if active_page == "new_consultation":
        page_new_consultation()

    elif active_page == "dashboard":
        page_dashboard()

    elif active_page == "detail":
        page_consultation_detail()

    st.markdown("""
    <div class="app-footer">
        Solusi Mitra UMKM &nbsp;&bull;&nbsp; Platform Konsultasi Bisnis untuk UMKM Indonesia<br>
        Dibangun dengan FastAPI, Streamlit, MySQL, SQLAlchemy
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
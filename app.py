import io
import os
import re

import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageEnhance

load_dotenv()

# ── HEIC support ─────────────────────────────────────────────────────────────
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

ACCEPTED_TYPES = ["jpg", "jpeg", "png"] + (["heic"] if HEIC_SUPPORTED else [])

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tax Ready PDF",
    page_icon="🧾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.stApp {
    background: #ffffff;
}
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"] {
    background: #ffffff !important;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 0 !important;
    max-width: 680px !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
footer { visibility: hidden !important; height: 0 !important; }
.stDeployButton { display: none; }

/* ── Navbar ── */
.trp-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 1.5rem;
    background: #ffffff;
}
.trp-nav-link {
    font-size: 0.8rem;
    font-weight: 500;
    color: #64748b;
    text-decoration: none;
    letter-spacing: -0.01em;
    transition: color 0.15s ease;
    white-space: nowrap;
    flex: 1;
}
.trp-nav-link:hover { color: #10b981; }
.trp-nav-link.right { text-align: right; }
.trp-navbar-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    flex: 2;
}
.trp-logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(16,185,129,0.15), 0 0 0 1px rgba(16,185,129,0.1);
}
.trp-logo svg { width: 24px; height: 24px; }
.trp-logo-name {
    font-size: 0.8rem;
    font-weight: 600;
    color: #1e293b;
    letter-spacing: -0.02em;
}

/* ── Hero ── */
.trp-hero {
    text-align: center;
    max-width: 700px;
    margin: 0 auto;
    padding: 2.5rem 1rem 2rem;
}
.trp-hero-title {
    font-size: 2.75rem;
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.04em;
    color: #0f172a;
    margin: 0 0 1.25rem;
}
.trp-hero-title .green { color: #10b981; }
.trp-hero-sub1 {
    font-size: 1.05rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 0.6rem;
    line-height: 1.45;
}
.trp-hero-sub2 {
    font-size: 0.88rem;
    font-weight: 400;
    color: #94a3b8;
    margin: 0;
    line-height: 1.65;
}
@media (max-width: 640px) {
    .trp-hero-title { font-size: 2rem; }
}

/* ── Legacy ── (kept for step/result reuse) */
.trp-header { padding: 0; }
.trp-title  { display: none; }
.trp-subtitle { display: none; }


/* ── Upload card shell ── */
.trp-card-top {
    background: #f8fff9;
    border: 2px dashed #a7f3d0;
    border-bottom: none;
    border-radius: 20px 20px 0 0;
    padding: 2.25rem 2rem 1.5rem;
    text-align: center;
}
.trp-card-bottom {
    border: 2px dashed #a7f3d0;
    border-top: none;
    border-radius: 0 0 20px 20px;
    padding: 0 1.5rem 1.5rem;
    background: #f8fff9;
}
.trp-cloud-icon {
    width: 56px;
    height: 56px;
    background: white;
    border-radius: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(16,185,129,0.15), 0 0 0 1px rgba(16,185,129,0.12);
    margin-bottom: 1.1rem;
}
.trp-cloud-icon svg { width: 28px; height: 28px; }
.trp-upload-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 0.3rem;
    letter-spacing: -0.02em;
}
.trp-upload-hint {
    font-size: 0.8rem;
    color: #94a3b8;
    margin: 0 0 1.1rem;
}
.trp-badge-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    flex-wrap: wrap;
}
.trp-badge {
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
}
/* divider between top and bottom */
.trp-card-divider {
    height: 1px;
    background: #d1fae5;
    margin: 0 1.5rem;
}
/* ── Streamlit uploader: strip all chrome, sit inside card ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
[data-testid="stFileUploader"] > div {
    background: transparent !important;
}
[data-testid="stFileUploader"] section {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}
[data-testid="stFileUploader"] section > div {
    border: none !important;
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"] {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
    min-height: 0 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
/* ── Upload "Datei wählen" button ── */
[data-testid="stFileUploader"] button {
    width: 100% !important;
    height: 44px !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: -0.01em !important;
    cursor: pointer !important;
    background: #10b981 !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 1px 3px rgba(16,185,129,0.35) !important;
    transition: background 0.18s ease, box-shadow 0.18s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
}
[data-testid="stFileUploader"] button::before {
    content: "📁";
    font-size: 0.9rem;
}
[data-testid="stFileUploader"] button:hover {
    background: #059669 !important;
    box-shadow: 0 4px 10px rgba(16,185,129,0.4) !important;
}
/* uploaded file name pill */
[data-testid="stFileUploaderFileName"] {
    background: #ecfdf5 !important;
    border-radius: 8px !important;
    padding: 4px 10px !important;
    font-size: 0.8rem !important;
    color: #059669 !important;
    margin-top: 0.5rem !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #10b981 !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(16,185,129,0.3) !important;
    letter-spacing: -0.01em !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #059669 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(16,185,129,0.4) !important;
}

/* ── Value props ── */
.trp-props {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.75rem;
    margin: 2rem 0 1.5rem;
}
.trp-prop {
    background: white;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    display: flex;
    align-items: flex-start;
    gap: 0.875rem;
    border: 1px solid #f1f5f9;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.trp-prop:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.07);
    transform: translateY(-1px);
}
.trp-prop-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}
.trp-prop-icon-1 { background: #eff6ff; }
.trp-prop-icon-2 { background: #fdf4ff; }
.trp-prop-icon-3 { background: #ecfdf5; }
.trp-prop-text strong {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 2px;
}
.trp-prop-text span {
    font-size: 0.8rem;
    color: #64748b;
    line-height: 1.45;
}

/* ── Result card ── */
.trp-result-card {
    background: white;
    border-radius: 20px;
    padding: 1.75rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin: 1.5rem 0;
}
.trp-result-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.trp-result-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.2);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(16,185,129,0.2); }
    50% { box-shadow: 0 0 0 6px rgba(16,185,129,0.1); }
}
.trp-result-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #059669;
    margin: 0;
}
.trp-filename-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 0.85rem;
    color: #1e293b;
    letter-spacing: -0.01em;
    margin-bottom: 1.25rem;
    word-break: break-all;
}
.trp-filename-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.4rem;
}

/* ── Error / Warning boxes ── */
.trp-error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    color: #dc2626;
    font-size: 0.875rem;
    font-weight: 500;
    margin: 1rem 0;
}
.trp-warning {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 12px;
    padding: 0.875rem 1.25rem;
    color: #92400e;
    font-size: 0.82rem;
    margin: 0 0 1.5rem;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
}

/* ── Preview image ── */
[data-testid="stImage"] img {
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    border: 1px solid #e2e8f0;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: #10b981 !important;
}
.stSpinner > div {
    border-top-color: #10b981 !important;
}

/* ── Suppress stray Streamlit widget labels ── */
[data-testid="stFileUploader"] label,
[data-baseweb="form-control"] > label,
.st-emotion-cache-1kyxreq,
[data-testid="InputInstructions"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* ── Footer ── */
.trp-footer-bar {
    margin-top: 6rem;
    border-top: 1px solid #e2e8f0;
    background: #f8fafc;
    padding: 1.5rem 0 1.25rem;
}
/* align all three columns to vertical center */
.trp-footer-bar [data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    background: #f8fafc;
    align-items: center !important;
}
.trp-footer-bar [data-testid="column"] {
    background: #f8fafc;
    padding: 0 0.25rem !important;
    display: flex;
    align-items: center;
}
/* left col: flex-start */
.trp-footer-bar [data-testid="column"]:first-child { justify-content: flex-start; }
/* center col: centered */
.trp-footer-bar [data-testid="column"]:nth-child(2) { justify-content: center; }
/* right col: flex-end */
.trp-footer-bar [data-testid="column"]:last-child  { justify-content: flex-end; }

.trp-footer-left {
    display: flex;
    align-items: center;
    gap: 7px;
    white-space: nowrap;
}
.trp-footer-logo-icon {
    width: 22px;
    height: 22px;
    background: linear-gradient(135deg, #ecfdf5, #d1fae5);
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 0 1px rgba(16,185,129,0.18);
    flex-shrink: 0;
}
.trp-footer-logo-icon svg { width: 13px; height: 13px; }
.trp-footer-logo-name {
    font-size: 0.75rem;
    font-weight: 700;
    color: #1e293b;
    letter-spacing: -0.02em;
}
.trp-footer-links {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1.75rem;
    white-space: nowrap;
}
.trp-footer-links a {
    font-size: 0.75rem;
    color: #64748b;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.15s ease;
}
.trp-footer-links a:hover { color: #10b981; }
.trp-footer-copy {
    font-size: 0.72rem;
    color: #94a3b8;
    text-align: right;
    white-space: nowrap;
    line-height: 1.4;
    margin: 0;
}

/* ── Mobile ── */
@media (max-width: 640px) {
    .trp-hero-title { font-size: 2rem; }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .trp-footer-bar [data-testid="stHorizontalBlock"] { flex-direction: column; gap: 0.75rem !important; }
    .trp-footer-bar [data-testid="column"] { justify-content: center !important; }
    .trp-footer-copy { text-align: center; }
}
</style>
""", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────────────
def get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "your_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY nicht gesetzt. Bitte trage deinen Key in die .env-Datei ein."
        )
    return key


def enhance_image(image: Image.Image) -> Image.Image:
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    return ImageEnhance.Contrast(image).enhance(1.2)


def ask_gemini(image: Image.Image, api_key: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "Extrahiere Firma, Datum und Bruttobetrag. "
        "Antworte NUR mit einem Dateinamen im Format: YYYY-MM-DD_Firma_Betrag. "
        "Ersetze Leerzeichen durch Unterstriche und Kommas durch Bindestriche."
    )
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    response = model.generate_content(
        [prompt, {"mime_type": "image/png", "data": buf.read()}]
    )
    return re.sub(r"[^\w\-.]", "_", response.text.strip())


def build_pdf(image: Image.Image) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    page_w, page_h = A4
    margin = 40
    img_w, img_h = image.size
    scale = min((page_w - 2 * margin) / img_w, (page_h - 2 * margin) / img_h, 1.0)
    draw_w, draw_h = img_w * scale, img_h * scale
    x, y = (page_w - draw_w) / 2, (page_h - draw_h) / 2

    buf_img = io.BytesIO()
    image.save(buf_img, format="PNG")
    buf_img.seek(0)

    buf_pdf = io.BytesIO()
    c = canvas.Canvas(buf_pdf, pagesize=A4)
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.drawImage(ImageReader(buf_img), x, y, width=draw_w, height=draw_h)
    c.save()
    return buf_pdf.getvalue()



# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<nav class="trp-navbar">
  <a class="trp-nav-link" href="mailto:hello@taxreadypdf.com">Contact</a>
  <div class="trp-navbar-center">
    <div class="trp-logo">
      <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="2" width="18" height="24" rx="3" fill="#d1fae5" stroke="#10b981" stroke-width="1.5"/>
        <path d="M9 9h8M9 13h8M9 17h5" stroke="#10b981" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="24" cy="24" r="7" fill="#10b981"/>
        <path d="M21 24l2 2 4-4" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <span class="trp-logo-name">Tax Ready PDF</span>
  </div>
  <a class="trp-nav-link right" href="#">Data Privacy</a>
</nav>

<!-- ── Hero ── -->
<div class="trp-hero">
  <h1 class="trp-hero-title">
    Dein Belegchaos.<br>
    <span class="green">Steuerberater-ready.</span><br>
    Sofort.
  </h1>
  <p class="trp-hero-sub1">
    In sauber formatierte, benannte PDF-Dateien – ohne Meckern vom Steuerberater.
  </p>
  <p class="trp-hero-sub2">
    Verwandle Fotos, Screenshots und PDFs in saubere A4-Dokumente.
    Bereit für DATEV&nbsp;&amp;&nbsp;Co. in Sekunden.
  </p>
</div>
""", unsafe_allow_html=True)


# ── API key warning ───────────────────────────────────────────────────────────
api_key_ok = bool(os.getenv("GEMINI_API_KEY", "").strip()) and \
             os.getenv("GEMINI_API_KEY", "").strip() != "your_api_key_here"
if not api_key_ok:
    st.markdown("""
    <div class="trp-warning">
      ⚠️ <span><strong>API-Key fehlt.</strong> Trage deinen <code>GEMINI_API_KEY</code>
      in die <code>.env</code>-Datei ein und starte die App neu.</span>
    </div>
    """, unsafe_allow_html=True)

# ── Upload card — top shell ───────────────────────────────────────────────────
heic_badge = '<span class="trp-badge">.HEIC</span>' if HEIC_SUPPORTED else ""
st.markdown(f"""
<div class="trp-card-top">
  <div class="trp-cloud-icon">
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 16V8M12 8L9 11M12 8L15 11" stroke="#10b981" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M7 18.5A4.5 4.5 0 0 1 7 9.5a.5.5 0 0 1 .05 0A5.5 5.5 0 0 1 17.5 10
               a3.5 3.5 0 0 1-.5 6.97" stroke="#10b981" stroke-width="1.6"
            stroke-linecap="round"/>
    </svg>
  </div>
  <p class="trp-upload-title">Dateien hier ablegen</p>
  <p class="trp-upload-hint">Unterstützt JPG, PNG, HEIC und PDF (max. 50 MB)</p>
  <div class="trp-badge-row">
    <span class="trp-badge">.JPG</span>
    <span class="trp-badge">.PNG</span>
    {heic_badge}
    <span class="trp-badge">.PDF</span>
  </div>
</div>
<div class="trp-card-divider"></div>
""", unsafe_allow_html=True)

# ── Upload card — bottom shell ────────────────────────────────────────────────
st.markdown('<div class="trp-card-bottom">', unsafe_allow_html=True)
uploaded = st.file_uploader(
    label="Datei wählen",
    type=ACCEPTED_TYPES,
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)

# ── Processing ────────────────────────────────────────────────────────────────
if uploaded:
    # Step 1 — read
    try:
        image_raw = Image.open(uploaded)
    except Exception as exc:
        st.markdown(
            f'<div class="trp-error">⚠️ Bild konnte nicht gelesen werden: {exc}</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    # Step 2 — enhance
    with st.spinner("Bild wird optimiert …"):
        image_enhanced = enhance_image(image_raw)

    # Step 3 — Gemini
    with st.spinner("KI analysiert den Beleg …"):
        try:
            api_key = get_api_key()
            suggested_name = ask_gemini(image_enhanced, api_key)
        except ValueError as exc:
            st.markdown(
                f'<div class="trp-error">🔑 {exc}</div>',
                unsafe_allow_html=True,
            )
            st.stop()
        except Exception as exc:
            st.markdown(
                f'<div class="trp-error">❌ Fehler bei der KI-Analyse: {exc}</div>',
                unsafe_allow_html=True,
            )
            st.stop()

    # Step 4 — PDF
    with st.spinner("PDF wird generiert …"):
        try:
            pdf_bytes = build_pdf(image_enhanced)
        except Exception as exc:
            st.markdown(
                f'<div class="trp-error">❌ PDF-Erstellung fehlgeschlagen: {exc}</div>',
                unsafe_allow_html=True,
            )
            st.stop()

    # ── Result card ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="trp-result-card">
      <div class="trp-result-header">
        <div class="trp-result-dot"></div>
        <p class="trp-result-title">Beleg erfolgreich verarbeitet</p>
      </div>
      <div class="trp-filename-label">Vorgeschlagener Dateiname</div>
      <div class="trp-filename-box">{suggested_name}.pdf</div>
    </div>
    """, unsafe_allow_html=True)

    # Preview
    st.image(image_enhanced, caption="Optimierte Vorschau", use_container_width=True)

    st.markdown("<div style='margin-top:1rem;'>", unsafe_allow_html=True)
    st.download_button(
        label="⬇ PDF herunterladen",
        data=pdf_bytes,
        file_name=f"{suggested_name}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Value propositions ────────────────────────────────────────────────────────
st.markdown("""
<div class="trp-props">
  <div class="trp-prop">
    <div class="trp-prop-icon trp-prop-icon-1">📋</div>
    <div class="trp-prop-text">
      <strong>Chaotische PDFs begradigen &amp; optimieren</strong>
      <span>Kontrast und Schärfe werden automatisch angepasst – perfekt für den Steuerberater.</span>
    </div>
  </div>
  <div class="trp-prop">
    <div class="trp-prop-icon trp-prop-icon-2">📷</div>
    <div class="trp-prop-text">
      <strong>Fotos (HEIC/JPG) in A4-Scans umwandeln</strong>
      <span>Handy-Fotos von Belegen werden sauber auf A4 zentriert – professionell und druckfertig.</span>
    </div>
  </div>
  <div class="trp-prop">
    <div class="trp-prop-icon trp-prop-icon-3">🤖</div>
    <div class="trp-prop-text">
      <strong>Direkte KI-Benennung (Datum_Firma_Betrag.pdf)</strong>
      <span>Gemini AI liest Datum, Firma und Betrag und benennt das PDF automatisch korrekt.</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="trp-footer-bar">', unsafe_allow_html=True)
fc_left, fc_center, fc_right = st.columns([1.5, 2.5, 2])

with fc_left:
    st.markdown("""
    <div class="trp-footer-left">
      <div class="trp-footer-logo-icon">
        <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="4" y="2" width="18" height="24" rx="3" fill="#d1fae5" stroke="#10b981" stroke-width="1.5"/>
          <path d="M9 9h8M9 13h8M9 17h5" stroke="#10b981" stroke-width="1.5" stroke-linecap="round"/>
          <circle cx="24" cy="24" r="7" fill="#10b981"/>
          <path d="M21 24l2 2 4-4" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <span class="trp-footer-logo-name">Tax Ready PDF</span>
    </div>
    """, unsafe_allow_html=True)

with fc_center:
    st.markdown("""
    <nav class="trp-footer-links">
      <a href="#">Impressum</a>
      <a href="#">Datenschutz</a>
      <a href="#">Kontakt</a>
    </nav>
    """, unsafe_allow_html=True)

with fc_right:
    st.markdown(
        '<p class="trp-footer-copy">© 2026 Tax Ready PDF. All rights reserved.</p>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

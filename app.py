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

/* ── Hero ── */
.trp-hero {
    text-align: center;
    max-width: 640px;
    margin: 0 auto;
    padding: 2.5rem 1rem 2rem;
}
.trp-hero-title {
    font-size: 3.25rem;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.04em;
    color: #111827;
    margin: 0 0 1.25rem;
}
.trp-hero-title .green { color: #5AA000; }
.trp-hero-sub {
    font-size: 1.125rem;
    font-weight: 400;
    color: #6b7280;
    margin: 0 auto;
    line-height: 1.6;
    max-width: 520px;
}
@media (max-width: 640px) {
    .trp-hero-title { font-size: 2.25rem; }
    .trp-hero-sub { font-size: 1rem; }
}

/* ── Legacy ── (kept for step/result reuse) */
.trp-header { padding: 0; }
.trp-title  { display: none; }
.trp-subtitle { display: none; }


/* ── Custom upload box ── */
.trp-upload-box {
    border: 2px dashed #5AA000;
    border-radius: 16px;
    background: #ffffff;
    padding: 40px 28px 36px;
    text-align: center;
    max-width: 480px;
    margin: 0 auto;
    transition: background 0.2s ease, border-color 0.2s ease;
}
.trp-upload-box.dragover {
    background: #EEF7DC;
    border-color: #3D7A00;
}
.trp-upload-icon-wrap {
    background: #5AA000;
    border-radius: 12px;
    width: 56px;
    height: 56px;
    margin: 0 auto 16px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.trp-upload-icon-wrap svg { width: 28px; height: 28px; }
.trp-upload-label {
    font-size: 1.1rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 6px;
}
.trp-upload-hint {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0 0 16px;
}
.trp-badge-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 24px;
}
.trp-badge {
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #374151;
    border: 1px solid #d1d5db;
    background: white;
}
.trp-upload-btns {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
}
.trp-btn-primary {
    background: #3D7A00;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 0.875rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: background 0.18s ease, box-shadow 0.18s ease;
    box-shadow: 0 1px 3px rgba(90,160,0,0.35);
}
.trp-btn-primary:hover { background: #2D5C00; box-shadow: 0 4px 12px rgba(90,160,0,0.4); }
.trp-btn-secondary {
    background: white;
    color: #374151;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 0.875rem;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: border-color 0.18s ease, background 0.18s ease;
}
.trp-btn-secondary:hover { border-color: #9ca3af; background: #f9fafb; }

/* ── Hide Streamlit's native uploader widget completely ── */
[data-testid="stFileUploader"] {
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* ── Uploaded file name pill (shown after selection) ── */
[data-testid="stFileUploaderFileName"] {
    background: #EEF7DC !important;
    border-radius: 8px !important;
    padding: 4px 10px !important;
    font-size: 0.8rem !important;
    color: #3D7A00 !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #5AA000 !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(90,160,0,0.3) !important;
    letter-spacing: -0.01em !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #3D7A00 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(90,160,0,0.4) !important;
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
    background: #5AA000;
    box-shadow: 0 0 0 3px rgba(90,160,0,0.2);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(90,160,0,0.2); }
    50% { box-shadow: 0 0 0 6px rgba(90,160,0,0.1); }
}
.trp-result-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #3D7A00;
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
    color: #5AA000 !important;
}
.stSpinner > div {
    border-top-color: #5AA000 !important;
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

/* ── Mobile ── */
@media (max-width: 640px) {
    .trp-hero-title { font-size: 2rem; }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .trp-upload-box { padding: 32px 20px; }
    .trp-upload-btns { flex-direction: column; align-items: stretch; }
    .trp-btn-primary, .trp-btn-secondary { justify-content: center; }
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
<style>
.custom-nav {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
  padding: 16px 40px;
  border-bottom: none;
  font-size: 14px;
}
</style>
<div class="custom-nav">
  <a href="#" style="color:#374151; text-decoration:none;">Kontakt</a>
  <div style="display:flex; align-items:center; gap:6px;">
    <span style="background:#EEF7DC; border-radius:6px; padding:4px 6px;">📄</span>
    <strong style="color:#111827; font-size:15px;">Tax Ready PDF</strong>
  </div>
  <a href="#" style="color:#374151; text-decoration:none;">Datenschutz</a>
</div>

<!-- ── Hero ── -->
<div class="trp-hero">
  <h1 class="trp-hero-title">
    Chaotische Belege.<br>
    <span class="green">Perfekt aufbereitet.</span><br>
    In Sekunden.
  </h1>
  <p class="trp-hero-sub">
    Fotos, Scans und PDFs werden automatisch auf A4 gebracht, optimiert und DATEV-ready benannt – ohne einen Handgriff.
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

# ── Custom upload box ─────────────────────────────────────────────────────────
heic_badge = '<span class="trp-badge">.HEIC</span>' if HEIC_SUPPORTED else ""
st.markdown(f"""
<div class="trp-upload-box" id="trp-dropzone">
  <div class="trp-upload-icon-wrap">
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 16V4M12 4L8 8M12 4L16 8" stroke="white" stroke-width="2.2"
            stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M4 20h16" stroke="white" stroke-width="2.2" stroke-linecap="round"/>
    </svg>
  </div>
  <p class="trp-upload-label">Dateien hier ablegen</p>
  <p class="trp-upload-hint">Mehrere Dateien gleichzeitig möglich – JPG, PNG, HEIC und PDF (max. 50MB)</p>
  <div class="trp-badge-row">
    <span class="trp-badge">.JPG</span>
    <span class="trp-badge">.PNG</span>
    {heic_badge}
    <span class="trp-badge">.PDF</span>
  </div>
  <div class="trp-upload-btns">
    <button class="trp-btn-primary" onclick="trpChooseFile(false)">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" stroke="white" stroke-width="2" stroke-linejoin="round"/><polyline points="14,2 14,8 20,8" stroke="white" stroke-width="2" stroke-linejoin="round"/></svg>
      Datei wählen
    </button>
    <button class="trp-btn-secondary" onclick="trpChooseFile(true)">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" stroke="#374151" stroke-width="2" stroke-linejoin="round"/><circle cx="12" cy="13" r="4" stroke="#374151" stroke-width="2"/></svg>
      Photo or scan directly
    </button>
  </div>
  <div style="margin-top:16px; font-size:13px; color:#6b7280; display:flex; gap:16px; justify-content:center; flex-wrap:wrap;">
    <span>✓ Automatisch A4-formatiert</span>
    <span>✓ KI-Benennung inklusive</span>
    <span>✓ DATEV-ready in Sekunden</span>
  </div>
</div>

<script>
(function() {{
  function getInput() {{
    return document.querySelector('[data-testid="stFileUploader"] input[type="file"]');
  }}
  window.trpChooseFile = function(camera) {{
    var input = getInput();
    if (!input) return;
    if (camera) {{
      input.setAttribute('capture', 'environment');
    }} else {{
      input.removeAttribute('capture');
    }}
    input.click();
  }};

  // Drag-and-drop support
  var zone = document.getElementById('trp-dropzone');
  if (zone) {{
    zone.addEventListener('dragover', function(e) {{
      e.preventDefault();
      zone.classList.add('dragover');
    }});
    zone.addEventListener('dragleave', function() {{
      zone.classList.remove('dragover');
    }});
    zone.addEventListener('drop', function(e) {{
      e.preventDefault();
      zone.classList.remove('dragover');
      var input = getInput();
      if (!input || !e.dataTransfer.files.length) return;
      // Use DataTransfer to set files on the hidden input
      try {{
        var dt = new DataTransfer();
        for (var i = 0; i < e.dataTransfer.files.length; i++) {{
          dt.items.add(e.dataTransfer.files[i]);
        }}
        input.files = dt.files;
        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
      }} catch(err) {{ console.warn('Drop fallback:', err); }}
    }});
  }}
}})();
</script>
""", unsafe_allow_html=True)

# ── Trust badges ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; justify-content:center; gap:32px; margin-top:24px; flex-wrap:wrap;">
  <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:#6B7280;">
    <span style="font-size:16px;">🇩🇪</span>
    <span><strong style="color:#374151;">Made in Germany</strong></span>
  </div>
  <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:#6B7280;">
    <span style="font-size:16px;">✅</span>
    <span><strong style="color:#374151;">Von Steuerberatern empfohlen</strong></span>
  </div>
  <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:#6B7280;">
    <span style="font-size:16px;">🔒</span>
    <span><strong style="color:#374151;">Dateien werden sofort gelöscht</strong></span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Hidden Streamlit file uploader (provides Python-side file handling) ────────
uploaded_files = st.file_uploader(
    label="Upload",
    type=ACCEPTED_TYPES,
    label_visibility="collapsed",
    accept_multiple_files=True,
)

# ── Processing ────────────────────────────────────────────────────────────────
if uploaded_files:
    n = len(uploaded_files)
    header_label = "Beleg verarbeiten …" if n == 1 else f"{n} Belege verarbeiten …"

    st.markdown(f"""
    <div class="trp-result-card">
      <div class="trp-result-header">
        <div class="trp-result-dot"></div>
        <p class="trp-result-title">{header_label}</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    results = []  # list of (original_name, suggested_name, pdf_bytes, error)

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        api_key = get_api_key()
    except ValueError as exc:
        st.markdown(f'<div class="trp-error">🔑 {exc}</div>', unsafe_allow_html=True)
        st.stop()

    for i, uploaded_file in enumerate(uploaded_files):
        status_text.markdown(
            f'<p style="text-align:center; color:#6b7280; font-size:0.875rem;">'
            f'Verarbeite {i+1} / {n}: <strong>{uploaded_file.name}</strong></p>',
            unsafe_allow_html=True,
        )

        # Step 1 — read
        try:
            image_raw = Image.open(uploaded_file)
        except Exception as exc:
            results.append((uploaded_file.name, None, None, str(exc)))
            progress_bar.progress((i + 1) / n)
            continue

        # Step 2 — enhance
        image_enhanced = enhance_image(image_raw)

        # Step 3 — Gemini
        try:
            suggested_name = ask_gemini(image_enhanced, api_key)
        except Exception as exc:
            results.append((uploaded_file.name, None, None, f"KI-Fehler: {exc}"))
            progress_bar.progress((i + 1) / n)
            continue

        # Step 4 — PDF
        try:
            pdf_bytes = build_pdf(image_enhanced)
        except Exception as exc:
            results.append((uploaded_file.name, None, None, f"PDF-Fehler: {exc}"))
            progress_bar.progress((i + 1) / n)
            continue

        results.append((uploaded_file.name, suggested_name, pdf_bytes, None))
        progress_bar.progress((i + 1) / n)

    status_text.empty()

    # ── Results table ─────────────────────────────────────────────────────────
    ok = [r for r in results if r[3] is None]
    errors = [r for r in results if r[3] is not None]

    if ok:
        success_label = "Beleg bereit" if len(ok) == 1 else f"{len(ok)} Belege bereit"
        st.markdown(f"""
        <div class="trp-result-card">
          <div class="trp-result-header">
            <div class="trp-result-dot"></div>
            <p class="trp-result-title">✓ {success_label}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        for orig_name, suggested_name, pdf_bytes, _ in ok:
            col_name, col_btn = st.columns([3, 1])
            with col_name:
                st.markdown(
                    f'<div class="trp-filename-box" style="margin:0;">'
                    f'<span style="color:#9ca3af; font-size:0.7rem; display:block; margin-bottom:2px;">{orig_name}</span>'
                    f'{suggested_name}.pdf</div>',
                    unsafe_allow_html=True,
                )
            with col_btn:
                st.download_button(
                    label="⬇ PDF",
                    data=pdf_bytes,
                    file_name=f"{suggested_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"dl_{suggested_name}",
                )

    for orig_name, _, __, error in errors:
        st.markdown(
            f'<div class="trp-error">⚠️ <strong>{orig_name}</strong>: {error}</div>',
            unsafe_allow_html=True,
        )

st.markdown("""
<div style="max-width:580px; margin:40px auto 120px; text-align:center;
font-size:12px; color:#9CA3AF; line-height:1.6;">
  Wir nutzen die Gemini API (Google) zur automatischen Texterkennung
  und Benennung Ihrer Belege. Die Verarbeitung erfolgt temporär –
  Ihre Dateien werden nach dem Download sofort gelöscht.
  Wir können jedoch nicht ausschließen, dass hochgeladene Inhalte
  vom KI-Anbieter verarbeitet werden.
  <strong>Bitte laden Sie keine personenbezogenen Dokumente hoch</strong>
  – geeignet sind Kassenbons, Quittungen und allgemeine Einkaufsbelege.
  Mit der Nutzung stimmen Sie unserer
  <a href="#" style="color:#9CA3AF;">Datenschutzerklärung</a> zu.
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Break footer out of Streamlit container */
[data-testid="stAppViewContainer"] > section > div {
  padding-bottom: 0 !important;
}
.footer-wrap {
  width: 100vw;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  background: #F9FAFB;
  border-top: 1px solid #E5E7EB;
  padding: 20px 48px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #6B7280;
  margin-top: 80px;
}
</style>
<div class="footer-wrap">
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="background:#EEF7DC;border-radius:4px;padding:2px 6px;">📄</span>
    <strong style="color:#111827;">Tax Ready PDF</strong>
  </div>
  <div style="display:flex;gap:24px;">
    <a href="#" style="color:#6B7280;text-decoration:none;">Impressum</a>
    <a href="#" style="color:#6B7280;text-decoration:none;">Datenschutz</a>
    <a href="#" style="color:#6B7280;text-decoration:none;">Kontakt</a>
  </div>
  <div>© 2024 Tax Ready PDF. All rights reserved.</div>
</div>
""", unsafe_allow_html=True)

import io
import os
import re
import base64

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
    page_title="ChaosPDF – Belege einfach bändigen",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Routing ───────────────────────────────────────────────────────────────────
page = st.query_params.get("page", "home")

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
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
footer { visibility: hidden !important; height: 0 !important; }
.stDeployButton { display: none; }

/* ── Hero ── */
.trp-hero {
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
    padding: 2.5rem 1rem 2rem;
}
.trp-hero-title {
    font-size: 4rem;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.04em;
    color: #111827;
    margin: 0 0 1.25rem;
}
.trp-hero-title .green { color: #5AA000; }
.trp-hero-sub1 {
    font-size: 1.5rem;
    font-weight: 400;
    color: #374151;
    margin: 0 auto;
    line-height: 1.6;
    max-width: 800px;
    text-align: center;
}
.trp-hero-sub2 {
    font-size: 1.2rem;
    font-weight: 400;
    color: #6b7280;
    margin: 0 auto;
    line-height: 1.6;
    max-width: 800px;
    text-align: center;
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
    max-width: 600px;
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
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 6px;
}
.trp-upload-hint {
    font-size: 1.1rem;
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
    padding: 15px 30px;
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
    padding: 15px 30px;
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
    .trp-hero-title { font-size: 2.5rem; }
    .trp-hero-sub1 { font-size: 1.2rem; }
    .trp-hero-sub2 { font-size: 1rem; }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .trp-upload-box { padding: 32px 20px; }
    .trp-upload-btns { flex-direction: column; align-items: stretch; }
    .trp-btn-primary, .trp-btn-secondary { justify-content: center; }
}
@media (max-width: 768px) {
    .hero-title { font-size: 36px !important; }
    .upload-box { padding: 24px 16px !important; }
    .trust-badges { flex-direction: column; gap: 12px !important; }
    .custom-nav { gap: 24px !important; padding: 12px 16px !important; }
    .custom-footer { flex-direction: column; gap: 8px !important;
                     text-align: center; padding: 16px !important; }
    .footer-wrap { flex-direction: column; gap: 8px !important; }
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


def load_logo_base64(path="logo.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return ""

base64_logo = load_logo_base64()

# ── Shared Navbar ─────────────────────────────────────────────────────────────
nav_html = f'''
<div style="display:flex; justify-content:center; align-items:center; gap:60px; padding:12px 40px;">
  <a href="?page=home" target="_top" style="color:#374151; text-decoration:none; font-weight:600;">Kontakt</a>
  <a href="?page=home" target="_top" style="border:0; display:block;">
    <img src="data:image/png;base64,{base64_logo}" style="width:140px; height:140px; object-fit:contain; display:block; border:0;">
  </a>
  <a href="?page=datenschutz" target="_top" style="color:#374151; text-decoration:none; font-weight:600;">Datenschutz</a>
</div>
'''
st.markdown(nav_html, unsafe_allow_html=True)


# ── Page: Home ────────────────────────────────────────────────────────────────
if page == "home":

    st.markdown("""
    <div class="trp-hero">
      <div style="text-align: center;">
        <h1 class="trp-hero-title">
          Dein Belegchaos.<br>
          <span class="green">Perfekt aufbereitet.</span><br>
          Sofort.
        </h1>
      </div>
      <p style="font-size:18px; color:#4B5563; text-align:center; max-width:560px; margin:0 auto 8px; line-height:1.6;">
        Kassenbons, Fotos und Scans landen oft unleserlich beim Steuerberater –
        schlecht gescannt, falsch benannt, nicht A4-formatiert.
      </p>
      <p style="font-size:18px; color:#5AA000; font-weight:600; text-align:center; margin:0 auto 32px;">
        ChaosPDF löst das in Sekunden – automatisch und DATEV-ready.
      </p>
    </div>
    """, unsafe_allow_html=True)

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

    uploaded_files = st.file_uploader(
        label="Upload",
        type=ACCEPTED_TYPES,
        label_visibility="collapsed",
        accept_multiple_files=True,
    )

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

        results = []
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

            try:
                image_raw = Image.open(uploaded_file)
            except Exception as exc:
                results.append((uploaded_file.name, None, None, str(exc)))
                progress_bar.progress((i + 1) / n)
                continue

            image_enhanced = enhance_image(image_raw)

            try:
                suggested_name = ask_gemini(image_enhanced, api_key)
            except Exception as exc:
                results.append((uploaded_file.name, None, None, f"KI-Fehler: {exc}"))
                progress_bar.progress((i + 1) / n)
                continue

            try:
                pdf_bytes = build_pdf(image_enhanced)
            except Exception as exc:
                results.append((uploaded_file.name, None, None, f"PDF-Fehler: {exc}"))
                progress_bar.progress((i + 1) / n)
                continue

            results.append((uploaded_file.name, suggested_name, pdf_bytes, None))
            progress_bar.progress((i + 1) / n)

        status_text.empty()

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
      <a href="?page=datenschutz" target="_top" style="color:#9CA3AF;">Datenschutzerklärung</a> zu.
    </div>
    """, unsafe_allow_html=True)


# ── Page: Impressum ───────────────────────────────────────────────────────────
elif page == "impressum":

    st.markdown("""
    <div style="max-width:680px; margin:48px auto 80px; padding:0 20px;">

      <a href="?page=home" target="_top" style="color:#5AA000; text-decoration:none; font-size:14px;">← Zurück</a>

      <h1 style="font-size:2rem; font-weight:800; color:#111827; margin:24px 0 8px;">Impressum</h1>
      <p style="font-size:14px; color:#6B7280; margin:0 0 40px;">Angaben gemäß § 5 TMG und § 2 DDG</p>

      <div style="margin-bottom:32px; font-size:15px; color:#4B5563; line-height:1.8;">
        <p style="font-weight:700; color:#111827; margin:0 0 8px;">Betreiber &amp; Verantwortlicher:</p>
        Chris Hahn<br>
        Donaustraße 44<br>
        12043 Berlin<br>
        Deutschland
      </div>

      <div style="margin-bottom:32px; font-size:15px; color:#4B5563; line-height:1.8;">
        <p style="font-weight:700; color:#111827; margin:0 0 8px;">Kontakt:</p>
        E-Mail: <a href="mailto:c@ckxh.eu" style="color:#5AA000;">c@ckxh.eu</a><br>
        Tel: +49 174 2095971<br>
        <span style="font-size:13px; color:#6B7280;">(Keine Support-Hotline. Für Fragen bitte per E-Mail melden.)</span>
      </div>

      <div style="margin-bottom:32px; font-size:15px; color:#4B5563; line-height:1.8;">
        <p style="font-weight:700; color:#111827; margin:0 0 8px;">Technologie &amp; Drittanbieter:</p>
        ChaosPDF nutzt zur automatischen Texterkennung, Dokumentenanalyse
        und Benennung von Belegen die Gemini API von Google LLC,
        1600 Amphitheatre Parkway, Mountain View, CA 94043, USA.<br>
        Mit der Nutzung des Dienstes stimmen Sie der temporären Übermittlung
        Ihrer hochgeladenen Dateien an Google-Server zu.<br>
        Wir empfehlen, keine personenbezogenen Dokumente hochzuladen.<br>
        Weitere Informationen:
        <a href="https://policies.google.com/privacy" target="_blank" style="color:#5AA000;">https://policies.google.com/privacy</a>
      </div>

      <div style="margin-bottom:32px; font-size:15px; color:#4B5563; line-height:1.8;">
        <p style="font-weight:700; color:#111827; margin:0 0 8px;">Hinweis zur Online-Streitbeilegung (ODR):</p>
        Die EU-Kommission stellt eine Plattform zur Online-Streitbeilegung bereit:<br>
        <a href="https://ec.europa.eu/consumers/odr" target="_blank" style="color:#5AA000;">https://ec.europa.eu/consumers/odr</a><br>
        Wir sind nicht verpflichtet und nicht bereit, an einem
        Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.
      </div>

      <div style="margin-bottom:32px; font-size:15px; color:#4B5563; line-height:1.8;">
        <p style="font-weight:700; color:#111827; margin:0 0 8px;">Weitere Hinweise:</p>
        ChaosPDF ist ein Onlinedienst zur automatischen Aufbereitung
        von Belegen und Dokumenten. Der Dienst nutzt KI-Technologie
        zur Texterkennung und Formatierung.
      </div>

    </div>
    """, unsafe_allow_html=True)


# ── Page: Datenschutz ─────────────────────────────────────────────────────────
elif page == "datenschutz":

    st.markdown("""
    <div style="max-width:680px; margin:48px auto 80px; padding:0 20px; font-size:15px; color:#4B5563; line-height:1.8;">

      <a href="?page=home" target="_top" style="color:#5AA000; text-decoration:none; font-size:14px;">← Zurück</a>

      <h1 style="font-size:2rem; font-weight:800; color:#111827; margin:24px 0 4px;">Datenschutzerklärung</h1>
      <p style="color:#6B7280; font-size:14px; margin:0 0 40px;">Stand: März 2026</p>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">1. Verantwortlicher</p>
        Chris Hahn<br>Donaustraße 44<br>12043 Berlin<br>
        E-Mail: <a href="mailto:c@ckxh.eu" style="color:#5AA000;">c@ckxh.eu</a>
      </div>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">2. Allgemeines</p>
        Der Schutz Ihrer Daten ist uns wichtig. Diese Erklärung informiert Sie
        darüber, welche Daten wir erheben, wie wir sie verarbeiten und welche
        Rechte Sie haben. Die Nutzung von ChaosPDF ist grundsätzlich ohne
        Angabe personenbezogener Daten möglich.
      </div>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">3. Erhebung allgemeiner Zugriffsdaten</p>
        Beim Aufruf unserer Website werden automatisch technische Zugriffsdaten
        erfasst (IP-Adresse, Browsertyp, Betriebssystem, Datum/Uhrzeit).
        Diese Daten dienen ausschließlich der technischen Bereitstellung
        des Dienstes und werden nicht zur Identifikation von Personen genutzt.
      </div>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">4. Verarbeitung hochgeladener Dateien</p>
        Zur Nutzung von ChaosPDF laden Sie Dateien hoch (Fotos, Scans, PDFs).
        Diese werden ausschließlich zur Verarbeitung Ihrer Anfrage verwendet
        und unmittelbar nach dem Download gelöscht. Es erfolgt keine dauerhafte
        Speicherung, keine Auswertung und keine Weitergabe an Dritte außer
        den nachfolgend genannten Auftragsverarbeitern.<br><br>
        Wir empfehlen ausdrücklich, keine personenbezogenen Dokumente
        hochzuladen. Geeignet sind Kassenbons, Quittungen und allgemeine
        Einkaufsbelege.
      </div>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">5. Einsatz der Google Gemini API</p>
        Zur KI-gestützten Texterkennung, automatischen Benennung und
        Optimierung Ihrer Belege nutzen wir die Gemini API von:<br><br>
        Google LLC<br>1600 Amphitheatre Parkway<br>Mountain View, CA 94043, USA<br><br>
        Hochgeladene Dateien werden zur Verarbeitung temporär an
        Google-Server übermittelt. Google verarbeitet diese Daten
        gemäß seiner Datenschutzrichtlinie:<br>
        <a href="https://policies.google.com/privacy" target="_blank" style="color:#5AA000;">https://policies.google.com/privacy</a><br><br>
        Die Übermittlung in die USA erfolgt auf Basis der
        EU-Standardvertragsklauseln (Art. 46 Abs. 2 lit. c DSGVO).
      </div>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">6. Hosting</p>
        ChaosPDF wird gehostet von:<br><br>
        Vercel Inc.<br>340 Pine Street, Suite 900<br>San Francisco, CA 94104, USA<br><br>
        Beim Aufruf der Website verarbeitet Vercel technische Zugriffsdaten.
        Weitere Informationen:
        <a href="https://vercel.com/legal/privacy-policy" target="_blank" style="color:#5AA000;">https://vercel.com/legal/privacy-policy</a><br>
        Die Übermittlung erfolgt ebenfalls auf Basis der EU-Standardvertragsklauseln.
      </div>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">7. Cookies</p>
        ChaosPDF verwendet keine Tracking-Cookies und keine Werbecookies.
        Es werden ausschließlich technisch notwendige Daten verarbeitet.
      </div>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">8. Ihre Rechte (Art. 15–22 DSGVO)</p>
        Sie haben das Recht auf:
        <ul style="margin:8px 0 12px; padding-left:20px;">
          <li>Auskunft über gespeicherte Daten</li>
          <li>Berichtigung unrichtiger Daten</li>
          <li>Löschung Ihrer Daten</li>
          <li>Einschränkung der Verarbeitung</li>
          <li>Datenübertragbarkeit</li>
          <li>Widerspruch gegen die Verarbeitung</li>
        </ul>
        Zur Ausübung Ihrer Rechte wenden Sie sich an:
        <a href="mailto:c@ckxh.eu" style="color:#5AA000;">c@ckxh.eu</a>
      </div>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">9. Beschwerderecht</p>
        Sie haben das Recht, sich bei einer Datenschutzaufsichtsbehörde
        zu beschweren. Zuständig für Berlin:<br><br>
        Berliner Beauftragte für Datenschutz und Informationsfreiheit<br>
        Friedrichstr. 219, 10969 Berlin<br>
        <a href="https://www.datenschutz-berlin.de" target="_blank" style="color:#5AA000;">https://www.datenschutz-berlin.de</a>
      </div>

      <div style="margin-bottom:28px;">
        <p style="font-weight:700; color:#111827; margin:0 0 6px;">10. Änderungen</p>
        Wir behalten uns vor, diese Datenschutzerklärung bei Bedarf
        anzupassen. Die jeweils aktuelle Version ist auf dieser Seite abrufbar.
      </div>

    </div>
    """, unsafe_allow_html=True)


# ── Shared Footer ─────────────────────────────────────────────────────────────
st.markdown(f'''
<div style="
  width: 100vw;
  position: relative;
  left: 50%;
  margin-left: -50vw;
  background: #D6D8D6;
  margin-top: 80px;
  padding: 24px 48px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #6B7280;
  box-sizing: border-box;
">
  <img src="data:image/png;base64,{base64_logo}" style="width:100px; height:100px; object-fit:contain; display:block;" alt="ChaosPDF Logo">
  <div style="display:flex; gap:24px;">
    <a href="?page=impressum" target="_top" style="color:#6B7280; text-decoration:none;">Impressum</a>
    <a href="?page=datenschutz" target="_top" style="color:#6B7280; text-decoration:none;">Datenschutz</a>
    <a href="#" style="color:#6B7280; text-decoration:none;">Kontakt</a>
  </div>
  <span>© 2026 ChaosPDF</span>
</div>
''', unsafe_allow_html=True)

import base64
import streamlit as st

st.set_page_config(
    page_title="Impressum – ChaosPDF",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_logo_base64(path="logo.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return ""


base64_logo = load_logo_base64()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

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
#MainMenu, footer, header { visibility: hidden; }
footer { visibility: hidden !important; height: 0 !important; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Navbar ──────────────────────────────────────────────────────────────────
nav_html = f'''
<div style="display:flex; justify-content:center; align-items:center; gap:60px; padding:12px 40px;">
  <a href="#" style="color:#374151; text-decoration:none; font-weight:600;">Kontakt</a>
  <a href="/" target="_top" style="border:0;"><img src="data:image/png;base64,{base64_logo}" style="width:140px; height:140px; object-fit:contain; display:block; border:0;"></a>
  <a href="/datenschutz" target="_top" style="color:#374151; text-decoration:none; font-weight:600;">Datenschutz</a>
</div>
'''
st.markdown(nav_html, unsafe_allow_html=True)

# ── Content ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:680px; margin:48px auto 80px; padding:0 24px;">

  <h1 style="font-size:2rem; font-weight:800; color:#111827; margin:0 0 8px;">Impressum</h1>
  <p style="font-size:14px; color:#6B7280; margin:0 0 40px;">
    Angaben gemäß § 5 TMG und § 2 DDG
  </p>

  <div style="margin-bottom:32px;">
    <p style="font-weight:700; color:#111827; font-size:15px; margin:0 0 8px;">
      Betreiber &amp; Verantwortlicher:
    </p>
    <p style="font-size:15px; color:#4B5563; line-height:1.8; margin:0;">
      Chris Hahn<br>
      Donaustraße 44<br>
      12043 Berlin<br>
      Deutschland
    </p>
  </div>

  <div style="margin-bottom:32px;">
    <p style="font-weight:700; color:#111827; font-size:15px; margin:0 0 8px;">Kontakt:</p>
    <p style="font-size:15px; color:#4B5563; line-height:1.8; margin:0;">
      E-Mail: <a href="mailto:c@ckxh.eu" style="color:#5AA000;">c@ckxh.eu</a><br>
      Tel: +49 174 2095971<br>
      <span style="font-size:13px; color:#6B7280;">
        (Keine Support-Hotline. Für Fragen bitte per E-Mail melden.)
      </span>
    </p>
  </div>

  <div style="margin-bottom:32px;">
    <p style="font-weight:700; color:#111827; font-size:15px; margin:0 0 8px;">
      Technologie &amp; Drittanbieter:
    </p>
    <p style="font-size:15px; color:#4B5563; line-height:1.8; margin:0;">
      ChaosPDF nutzt zur automatischen Texterkennung, Dokumentenanalyse
      und Benennung von Belegen die Gemini API von Google LLC,
      1600 Amphitheatre Parkway, Mountain View, CA 94043, USA.<br>
      Mit der Nutzung des Dienstes stimmen Sie der temporären Übermittlung
      Ihrer hochgeladenen Dateien an Google-Server zu.<br>
      Wir empfehlen, keine personenbezogenen Dokumente hochzuladen.<br>
      Weitere Informationen:
      <a href="https://policies.google.com/privacy" target="_blank"
         style="color:#5AA000;">https://policies.google.com/privacy</a>
    </p>
  </div>

  <div style="margin-bottom:32px;">
    <p style="font-weight:700; color:#111827; font-size:15px; margin:0 0 8px;">
      Hinweis zur Online-Streitbeilegung (ODR):
    </p>
    <p style="font-size:15px; color:#4B5563; line-height:1.8; margin:0;">
      Die EU-Kommission stellt eine Plattform zur Online-Streitbeilegung bereit:<br>
      <a href="https://ec.europa.eu/consumers/odr" target="_blank"
         style="color:#5AA000;">https://ec.europa.eu/consumers/odr</a><br>
      Wir sind nicht verpflichtet und nicht bereit, an einem
      Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.
    </p>
  </div>

  <div style="margin-bottom:32px;">
    <p style="font-weight:700; color:#111827; font-size:15px; margin:0 0 8px;">
      Weitere Hinweise:
    </p>
    <p style="font-size:15px; color:#4B5563; line-height:1.8; margin:0;">
      ChaosPDF ist ein Onlinedienst zur automatischen Aufbereitung
      von Belegen und Dokumenten. Der Dienst nutzt KI-Technologie
      zur Texterkennung und Formatierung.
    </p>
  </div>

</div>
""", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────
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
    <a href="/impressum" target="_top" style="color:#6B7280; text-decoration:none;">Impressum</a>
    <a href="/datenschutz" target="_top" style="color:#6B7280; text-decoration:none;">Datenschutz</a>
    <a href="#" style="color:#6B7280; text-decoration:none;">Kontakt</a>
  </div>
  <span>© 2026 ChaosPDF</span>
</div>
''', unsafe_allow_html=True)

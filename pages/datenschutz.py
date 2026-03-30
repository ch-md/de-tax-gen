import base64
import streamlit as st

st.set_page_config(
    page_title="Datenschutz – ChaosPDF",
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

# ── Navbar ───────────────────────────────────────────────────────────────────
nav_html = f'''
<div style="display:flex; justify-content:center; align-items:center; gap:60px; padding:12px 40px;">
  <a href="#" style="color:#374151; text-decoration:none; font-weight:600;">Kontakt</a>
  <a href="/" target="_top" style="border:0;">
    <img src="data:image/png;base64,{base64_logo}" style="width:140px; height:140px; object-fit:contain; display:block; border:0;">
  </a>
  <a href="/datenschutz" target="_top" style="color:#374151; text-decoration:none; font-weight:600;">Datenschutz</a>
</div>
'''
st.markdown(nav_html, unsafe_allow_html=True)

# ── Content ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:680px; margin:48px auto 80px; padding:0 20px; font-size:15px; color:#4B5563; line-height:1.8;">

  <h1 style="font-size:2rem; font-weight:800; color:#111827; margin:0 0 4px;">Datenschutzerklärung</h1>
  <p style="color:#6B7280; font-size:14px; margin:0 0 40px;">Stand: März 2026</p>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">1. Verantwortlicher</p>
    <p style="margin:0;">
      Chris Hahn<br>
      Donaustraße 44<br>
      12043 Berlin<br>
      E-Mail: <a href="mailto:c@ckxh.eu" style="color:#5AA000;">c@ckxh.eu</a>
    </p>
  </div>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">2. Allgemeines</p>
    <p style="margin:0;">
      Der Schutz Ihrer Daten ist uns wichtig. Diese Erklärung informiert Sie
      darüber, welche Daten wir erheben, wie wir sie verarbeiten und welche
      Rechte Sie haben. Die Nutzung von ChaosPDF ist grundsätzlich ohne
      Angabe personenbezogener Daten möglich.
    </p>
  </div>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">3. Erhebung allgemeiner Zugriffsdaten</p>
    <p style="margin:0;">
      Beim Aufruf unserer Website werden automatisch technische Zugriffsdaten
      erfasst (IP-Adresse, Browsertyp, Betriebssystem, Datum/Uhrzeit).
      Diese Daten dienen ausschließlich der technischen Bereitstellung
      des Dienstes und werden nicht zur Identifikation von Personen genutzt.
    </p>
  </div>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">4. Verarbeitung hochgeladener Dateien</p>
    <p style="margin:0 0 12px;">
      Zur Nutzung von ChaosPDF laden Sie Dateien hoch (Fotos, Scans, PDFs).
      Diese werden ausschließlich zur Verarbeitung Ihrer Anfrage verwendet
      und unmittelbar nach dem Download gelöscht. Es erfolgt keine dauerhafte
      Speicherung, keine Auswertung und keine Weitergabe an Dritte außer
      den nachfolgend genannten Auftragsverarbeitern.
    </p>
    <p style="margin:0;">
      Wir empfehlen ausdrücklich, keine personenbezogenen Dokumente
      hochzuladen. Geeignet sind Kassenbons, Quittungen und allgemeine
      Einkaufsbelege.
    </p>
  </div>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">5. Einsatz der Google Gemini API</p>
    <p style="margin:0 0 12px;">
      Zur KI-gestützten Texterkennung, automatischen Benennung und
      Optimierung Ihrer Belege nutzen wir die Gemini API von:
    </p>
    <p style="margin:0 0 12px;">
      Google LLC<br>
      1600 Amphitheatre Parkway<br>
      Mountain View, CA 94043, USA
    </p>
    <p style="margin:0 0 12px;">
      Hochgeladene Dateien werden zur Verarbeitung temporär an
      Google-Server übermittelt. Google verarbeitet diese Daten
      gemäß seiner Datenschutzrichtlinie:<br>
      <a href="https://policies.google.com/privacy" target="_blank" style="color:#5AA000;">https://policies.google.com/privacy</a>
    </p>
    <p style="margin:0;">
      Die Übermittlung in die USA erfolgt auf Basis der
      EU-Standardvertragsklauseln (Art. 46 Abs. 2 lit. c DSGVO).
    </p>
  </div>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">6. Hosting</p>
    <p style="margin:0 0 12px;">
      ChaosPDF wird gehostet von:
    </p>
    <p style="margin:0 0 12px;">
      Vercel Inc.<br>
      340 Pine Street, Suite 900<br>
      San Francisco, CA 94104, USA
    </p>
    <p style="margin:0;">
      Beim Aufruf der Website verarbeitet Vercel technische Zugriffsdaten.
      Weitere Informationen: <a href="https://vercel.com/legal/privacy-policy" target="_blank" style="color:#5AA000;">https://vercel.com/legal/privacy-policy</a><br>
      Die Übermittlung erfolgt ebenfalls auf Basis der EU-Standardvertragsklauseln.
    </p>
  </div>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">7. Cookies</p>
    <p style="margin:0;">
      ChaosPDF verwendet keine Tracking-Cookies und keine Werbecookies.
      Es werden ausschließlich technisch notwendige Daten verarbeitet.
    </p>
  </div>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">8. Ihre Rechte (Art. 15–22 DSGVO)</p>
    <p style="margin:0 0 8px;">Sie haben das Recht auf:</p>
    <ul style="margin:0 0 12px; padding-left:20px;">
      <li>Auskunft über gespeicherte Daten</li>
      <li>Berichtigung unrichtiger Daten</li>
      <li>Löschung Ihrer Daten</li>
      <li>Einschränkung der Verarbeitung</li>
      <li>Datenübertragbarkeit</li>
      <li>Widerspruch gegen die Verarbeitung</li>
    </ul>
    <p style="margin:0;">
      Zur Ausübung Ihrer Rechte wenden Sie sich an:
      <a href="mailto:c@ckxh.eu" style="color:#5AA000;">c@ckxh.eu</a>
    </p>
  </div>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">9. Beschwerderecht</p>
    <p style="margin:0 0 12px;">
      Sie haben das Recht, sich bei einer Datenschutzaufsichtsbehörde
      zu beschweren. Zuständig für Berlin:
    </p>
    <p style="margin:0;">
      Berliner Beauftragte für Datenschutz und Informationsfreiheit<br>
      Friedrichstr. 219, 10969 Berlin<br>
      <a href="https://www.datenschutz-berlin.de" target="_blank" style="color:#5AA000;">https://www.datenschutz-berlin.de</a>
    </p>
  </div>

  <div style="margin-bottom:28px;">
    <p style="font-weight:700; color:#111827; margin:0 0 6px;">10. Änderungen</p>
    <p style="margin:0;">
      Wir behalten uns vor, diese Datenschutzerklärung bei Bedarf
      anzupassen. Die jeweils aktuelle Version ist auf dieser Seite abrufbar.
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

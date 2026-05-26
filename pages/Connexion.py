import streamlit as st
import base64, os, random, string, smtplib, datetime, requests
import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- INITIALISATION FIREBASE ---
if not firebase_admin._apps:
    base_path = os.path.dirname(os.path.dirname(__file__))
    key_path = os.path.join(base_path, "serviceAccountKey.json")
    if os.path.exists(key_path):
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)

db = firestore.client()

from config import FIREBASE_WEB_API_KEY

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


st.set_page_config(page_title="AgroSmart – Connexion", layout="wide", initial_sidebar_state="collapsed")

# ── Navigation entrante ──
if "goto" in st.query_params:
    dest = st.query_params["goto"]
    if dest == "register":
        st.switch_page("pages/Inscription.py")

if st.session_state.get("reg_success"):
    st.toast(st.session_state["reg_success"], icon="✅")
    del st.session_state["reg_success"]


# ── Styles Streamlit ──
st.markdown("""
<style>
    #MainMenu, header, footer { visibility: hidden !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    .block-container {
        padding: 0 !important; margin: 0 !important;
        max-width: 100vw !important; margin-top: 0 !important;
    }
    html, body,
    [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="stApp"], section[data-testid="stMain"] > div,
    [data-testid="stVerticalBlock"], [data-testid="stVerticalBlockBorderWrapper"] {
        margin: 0 !important; padding: 0 !important; background: #ffffff !important;
    }
    iframe { display: block !important; background: #ffffff; }
</style>
""", unsafe_allow_html=True)

# ── Image blob ──
@st.cache_data
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = image_path.rsplit(".", 1)[-1]
        return f"data:image/{ext};base64,{b64}"
    return ""

IMAGE_PATH = "farm_bg.jpg"
bg_src = get_base64_image(IMAGE_PATH)
FALLBACK_BG = "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=900&q=80"
bg_url = f'url("{bg_src}")' if bg_src else f'url("{FALLBACK_BG}")'

# ══════════════════════════════════════
#  LOGIQUE RÉINITIALISATION MOT DE PASSE
# ══════════════════════════════════════
def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_reset_email(to_email: str, code: str) -> bool:
    try:
        from config import EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "AgroSmart – Code de réinitialisation"
        msg["From"]    = f"AgroSmart <{EMAIL_ADDRESS}>"
        msg["To"]      = to_email

        html_body = f"""
        <div style="font-family:Poppins,sans-serif;max-width:480px;margin:auto;background:#f8fdf9;
                    border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.1)">
          <div style="background:#1a4a35;padding:32px 40px;text-align:center">
            <h1 style="color:#fff;font-size:1.6rem;margin:0;display:flex;align-items:center;justify-content:center;gap:8px">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l2 8h-4l2 8-6-6 6-10z"/>
              </svg>
              AgroSmart
            </h1>
            <p style="color:#9dccaa;margin:6px 0 0;font-size:.85rem">
              Réinitialisation de mot de passe
            </p>
          </div>
          <div style="padding:36px 40px">
            <p style="color:#2d4a35;font-size:.95rem;line-height:1.6">
              Bonjour,<br><br>
              Vous avez demandé la réinitialisation de votre mot de passe AgroSmart.<br>
              Voici votre code de vérification valable <strong>10 minutes</strong> :
            </p>
            <div style="text-align:center;margin:28px 0">
              <span style="font-size:2.4rem;font-weight:800;letter-spacing:12px;
                           color:#1a4a35;background:#e8f5eb;padding:16px 28px;
                           border-radius:12px;display:inline-block">
                {code}
              </span>
            </div>
            <p style="color:#666;font-size:.82rem;line-height:1.5">
              Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.<br>
              Votre mot de passe ne sera pas modifié.
            </p>
          </div>
          <div style="background:#f0f4f0;padding:16px;text-align:center">
            <p style="color:#aaa;font-size:.72rem;margin:0">
              © 2026 AgroSmart
            </p>
          </div>
        </div>
        """
        msg.attach(MIMEText(html_body, "html"))

        import time
        start_time = time.time()
        
        with open("login_debug.log", "a") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] SMTP: Connexion à {SMTP_SERVER}:{SMTP_PORT}...\n")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            with open("login_debug.log", "a") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] SMTP: Connecté. ({time.time()-start_time:.2f}s). EHLO...\n")
            server.ehlo()
            
            with open("login_debug.log", "a") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] SMTP: STARTTLS... ({time.time()-start_time:.2f}s)\n")
            server.starttls()
            
            with open("login_debug.log", "a") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] SMTP: Login en cours... ({time.time()-start_time:.2f}s)\n")
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            
            with open("login_debug.log", "a") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] SMTP: Envoi à {to_email}... ({time.time()-start_time:.2f}s)\n")
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
            
        with open("login_debug.log", "a") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] SMTP: Terminé avec succès ! Temps total : {time.time()-start_time:.2f}s\n")
        return True
    except Exception as e:
        import time
        with open("login_debug.log", "a") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] SMTP ERROR: {e}\n")
        st.session_state["reset_error"] = str(e)
        return False

# ── Gestion des actions ──
action = st.query_params.get("action", "")

import time
with open("login_debug.log", "a") as f:
    f.write(f"[{time.strftime('%H:%M:%S')}] Connexion.py loaded. Action: '{action}', Session user: '{st.session_state.get('user', '')}'\n")

# ── Base de données en mémoire pour AJAX ──
@st.cache_resource
def get_reset_db():
    return {}

reset_db = get_reset_db()

# ── Gestion des actions AJAX ──
action = st.query_params.get("action", "")

if action == "forgot_ajax":
    email_to = st.query_params.get("email", "").strip()
    
    js_bcast = """
    <script>
    let p = window.parent;
    while(p) {
        p.postMessage({msg}, '*');
        if (p === window.top) break;
        p = p.parent;
    }
    </script>
    """
    
    try:
        from firebase_admin import auth
        user = auth.get_user_by_email(email_to)
        
        # L'utilisateur existe
        code = generate_code()
        expiry = datetime.datetime.now() + datetime.timedelta(minutes=10)
        reset_db[email_to] = {"code": code, "expiry": expiry}
        ok = send_reset_email(email_to, code)
        if ok:
            st.components.v1.html(js_bcast.replace("{msg}", "{type: 'forgot_result', success: true}"))
        else:
            st.components.v1.html(js_bcast.replace("{msg}", "{type: 'forgot_result', success: false, msg: 'Erreur lors de lenvoi du mail.'}"))
    except Exception as e:
        # UserNotFoundError ou autre erreur
        if "UserNotFoundError" in str(type(e).__name__) or "user not found" in str(e).lower():
            st.components.v1.html(js_bcast.replace("{msg}", "{type: 'forgot_result', success: false, msg: 'Aucun compte associé à cet email.'}"))
        else:
            st.components.v1.html(js_bcast.replace("{msg}", "{type: 'forgot_result', success: false, msg: 'Erreur lors de la vérification.'}"))
    st.stop()

if action == "verify_ajax":
    entered = st.query_params.get("code", "").strip()
    email_to = st.query_params.get("email", "").strip()
    stored_data = reset_db.get(email_to, {})
    stored  = stored_data.get("code", "")
    expiry  = stored_data.get("expiry", datetime.datetime.min)
    js_bcast = """<script>let p=window.parent;while(p){p.postMessage({msg}, '*');if(p===window.top)break;p=p.parent;}</script>"""
    if stored and entered == stored and datetime.datetime.now() < expiry:
        st.components.v1.html(js_bcast.replace("{msg}", "{type: 'verify_result', success: true}"))
    else:
        st.components.v1.html(js_bcast.replace("{msg}", "{type: 'verify_result', success: false, msg: 'Code incorrect ou expiré.'}"))
    st.stop()

if action == "reset_ajax":
    pwd = st.query_params.get("pwd", "")
    email = st.query_params.get("email", "").strip()
    code = st.query_params.get("code", "").strip()
    js_bcast = """<script>let p=window.parent;while(p){p.postMessage({msg}, '*');if(p===window.top)break;p=p.parent;}</script>"""
    
    stored_data = reset_db.get(email, {})
    stored  = stored_data.get("code", "")
    expiry  = stored_data.get("expiry", datetime.datetime.min)
    
    if stored and code == stored and datetime.datetime.now() < expiry:
        try:
            from firebase_admin import auth
            user = auth.get_user_by_email(email)
            auth.update_user(user.uid, password=pwd)
            if email in reset_db:
                del reset_db[email]
            st.components.v1.html(js_bcast.replace("{msg}", "{type: 'reset_result', success: true}"))
        except Exception as e:
            st.components.v1.html(js_bcast.replace("{msg}", "{type: 'reset_result', success: false, msg: 'Erreur lors de la réinitialisation.'}"))
    else:
        st.components.v1.html(js_bcast.replace("{msg}", "{type: 'reset_result', success: false, msg: 'Session invalide ou expirée.'}"))
    st.stop()

if action == "login_success":
    uid = st.query_params.get("uid", "").strip()
    if uid:
        st.session_state["user"] = uid
        st.session_state["show_success"] = "Connexion réussie ! Bienvenue sur AgroSmart."
        with open("login_debug.log", "a") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] Login success registered. User ID: {uid}\n")
    st.query_params.clear()
    st.rerun()



login_error     = st.session_state.get("login_error", "")
if "login_error" in st.session_state: del st.session_state["login_error"]

# Redirection si connecté
if st.session_state.get("user"):
    with open("login_debug.log", "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] Switching page to Tableau_de_bord.py\n")
    st.switch_page("pages/Tableau_de_bord.py")


html_code = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ height: 100%; width: 100%; margin: 0; padding: 0; }}
  body {{
    font-family: 'Poppins', sans-serif; background: #fff;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; padding: 24px;
  }}
  .wrapper {{ display: flex; align-items: center; justify-content: center; width: 100%; }}
  .card {{
    display: flex; width: 820px; min-height: 480px; border-radius: 24px;
    overflow: hidden; box-shadow: 0 24px 64px rgba(0,0,0,.18);
    position: relative; margin: 0 auto;
  }}
  .left {{ flex: 1; position: relative; background: #e8f0e8; overflow: hidden; }}
  .bubble {{ position: absolute; border-radius: 50%; background: rgba(255,255,255,.55); backdrop-filter: blur(4px); }}
  .bubble-1 {{ width:110px; height:110px; top:-30px;  left:-30px; }}
  .bubble-2 {{ width: 70px; height: 70px;  top: 30px; left:120px; opacity:.7; }}
  .bubble-3 {{ width: 90px; height: 90px;  bottom:60px; right:20px; opacity:.5; }}
  .bubble-4 {{ width: 50px; height: 50px;  bottom:20px; left:40px; opacity:.6; }}
  .photo-blob {{
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%); width: 88%; height: 88%;
    background-image: {bg_url}; background-size: cover; background-position: center;
    clip-path: polygon(30% 0%,70% 0%,100% 20%,100% 75%,75% 100%,25% 100%,0% 75%,0% 20%);
    border-radius: 40% 55% 50% 45% / 45% 40% 55% 50%;
    animation: morphBlob 8s ease-in-out infinite;
  }}
  @keyframes morphBlob {{
    0%,100% {{ border-radius: 40% 55% 50% 45% / 45% 40% 55% 50%; }}
    33%      {{ border-radius: 55% 40% 45% 55% / 50% 55% 40% 45%; }}
    66%      {{ border-radius: 45% 50% 55% 40% / 55% 45% 50% 40%; }}
  }}
  .right {{
    width: 360px; background: #1a4a35; padding: 48px 40px 40px;
    display: flex; flex-direction: column; justify-content: center; gap: 20px;
  }}
  .right h1 {{ color:#fff; font-size:2rem; font-weight:700; text-align:center; letter-spacing:.5px; }}
  .field-group {{ display: flex; flex-direction: column; gap: 6px; }}
  .field-group label {{ color:#d4e8d6; font-size:.88rem; font-weight:500; }}
  .input-wrap {{ position: relative; display: flex; align-items: center; }}
  .input-wrap input {{
    width:100%; padding:11px 40px 11px 38px; background:#e8f5eb; border:none;
    border-radius:8px; font-size:.9rem; font-family:'Poppins',sans-serif;
    color:#1a3a28; outline:none; transition:box-shadow .2s;
  }}
  .input-wrap input:focus {{ box-shadow: 0 0 0 2.5px #5cb87a; }}
  .input-wrap input::placeholder {{ color: #aac9b2; }}
  .icon-left {{ position:absolute; left:11px; color:#5a8a6a; font-size:1rem; pointer-events:none; }}
  .icon-right {{ position:absolute; right:11px; color:#5a8a6a; font-size:1rem; cursor:pointer; user-select:none; }}
  .options {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: .78rem;
    font-family: 'Poppins', sans-serif;
  }}
  .options label {{
    display: flex;
    align-items: center;
    gap: 6px;
    color: #ffffff;
    cursor: pointer;
  }}
  .options input[type=checkbox] {{
    accent-color: #5cb87a;
    width: 14px;
    height: 14px;
  }}
  #forgot-link {{
    color: #ffffff !important;
    text-decoration: underline;
    font-size: .78rem;
    font-family: 'Poppins', sans-serif;
    cursor: pointer;
  }}
  .btn-connect {{
    width:100%; padding:13px; background:#e8f5eb; color:#1a4a35; border:none;
    border-radius:9px; font-family:'Poppins',sans-serif; font-size:.95rem; font-weight:600;
    cursor:pointer; transition:background .2s,transform .1s,box-shadow .2s; letter-spacing:.3px;
  }}
  .btn-connect:hover {{ background:#c8eacc; box-shadow:0 4px 18px rgba(0,0,0,.15); transform:translateY(-1px); }}
  .btn-connect:active {{ transform:translateY(0); }}
  .signup {{ text-align:center; font-size:.78rem; color:#9dbfa4; }}
  .signup a {{ color:#d4e8d6; text-decoration:underline; font-weight:500; cursor:pointer; }}
  .signup a:hover {{ color:#fff; }}
  #feedback {{ text-align:center; font-size:.82rem; min-height:18px; color:#f08080; }}

  /* ── MODAL ── */
  .modal-backdrop {{
    display:none; position:fixed; inset:0;
    background:rgba(0,0,0,.6); backdrop-filter:blur(4px);
    z-index:100; align-items:center; justify-content:center;
  }}
  .modal-backdrop.open {{ display:flex; }}
  .modal {{
    background:#1a4a35; border-radius:20px; padding:36px 32px;
    width:340px; display:flex; flex-direction:column; gap:16px;
    box-shadow:0 16px 48px rgba(0,0,0,.4);
    border:1px solid rgba(255,255,255,.12);
    animation: popIn .3s ease both;
  }}
  @keyframes popIn {{
    from {{ opacity:0; transform:scale(.92) translateY(16px); }}
    to   {{ opacity:1; transform:scale(1) translateY(0); }}
  }}
  .modal h2 {{ color:#fff; font-size:1.2rem; font-weight:700; text-align:center; }}
  .modal p  {{ color:#c4dbc8; font-size:.82rem; text-align:center; line-height:1.5; }}
  .modal input {{
    width:100%; padding:11px 16px; background:#e8f5eb; border:none;
    border-radius:8px; font-size:.9rem; font-family:'Poppins',sans-serif;
    color:#1a3a28; outline:none; transition:box-shadow .2s; text-align:center;
    letter-spacing:6px; font-weight:700; font-size:1.1rem;
  }}
  .modal input:focus {{ box-shadow:0 0 0 2.5px #5cb87a; }}
  .modal input::placeholder {{ letter-spacing:normal; font-weight:400; font-size:.9rem; color:#aac9b2; }}
  .modal-btn {{
    width:100%; padding:12px; background:#e8f5eb; color:#1a4a35; border:none;
    border-radius:9px; font-family:'Poppins',sans-serif; font-size:.9rem; font-weight:600;
    cursor:pointer; transition:background .2s; letter-spacing:.3px;
  }}
  .modal-btn:hover {{ background:#c8eacc; }}
  .modal-btn.secondary {{
    background:transparent; color:#c4dbc8; border:1px solid rgba(255,255,255,.2);
  }}
  .modal-btn.secondary:hover {{ background:rgba(255,255,255,.08); }}
  .modal-feedback {{ text-align:center; font-size:.82rem; min-height:16px; color:#f08080; }}
  .modal-step {{ display:none; flex-direction:column; gap:14px; }}
  .modal-step.active {{ display:flex; }}
</style>
</head>
<body>

<div class="wrapper">
  <div class="card">
    <div class="left">
      <div class="bubble bubble-1"></div><div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div><div class="bubble bubble-4"></div>
      <div class="photo-blob"></div>
    </div>
    <div class="right">
      <h1>Connexion</h1>
      <div class="field-group">
        <label for="email">Adresse Email</label>
        <div class="input-wrap">
          <span class="icon-left">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
            </svg>
          </span>
          <input id="email" type="email" placeholder="exemple@email.com" autocomplete="email" required>
        </div>
      </div>
      <div class="field-group">
        <label for="password">Mot de passe</label>
        <div class="input-wrap">
          <span class="icon-left">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm3 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/>
            </svg>
          </span>
          <input id="password" type="password" placeholder="••••••••" required>
          <span class="icon-right" id="toggle-pwd-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
            </svg>
          </span>

        </div>
      </div>
      <div class="options">
        <label><input type="checkbox" id="remember"> Se souvenir de moi</label>
        <a id="forgot-link" href="javascript:void(0);" onclick="openForgot()">Mot de passe oublié ?</a>
      </div>
      <button class="btn-connect" id="login-btn" onclick="handleLogin()">Se connecter</button>

      <div id="feedback"></div>
      <p class="signup">Vous n'avez pas de compte ?
        <a href="/Inscription">Créez</a>
      </p>
    </div>
  </div>
</div>

<!-- ══ MODAL MOT DE PASSE OUBLIÉ ══ -->
<div class="modal-backdrop" id="modalBackdrop">
  <div class="modal">
    <h2 style="display:flex;align-items:center;gap:8px">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
      </svg>
      Mot de passe oublié
    </h2>

    <!-- Étape 1 : saisir l'email -->
    <div class="modal-step active" id="step1">
      <p>Entrez votre adresse email pour recevoir un code de vérification.</p>
      <div class="input-wrap" style="margin:0">
        <input id="resetEmail" type="email" placeholder="exemple@email.com">
      </div>
      <div class="modal-feedback" id="fb1"></div>
      <button class="modal-btn" id="send-code-btn" onclick="sendCode()">📨 Envoyer le code</button>
      <button class="modal-btn secondary" id="close-modal-btn" onclick="closeModal()">Annuler</button>

    </div>

    <!-- Étape 2 : saisir le code reçu -->
    <div class="modal-step" id="step2">
      <p id="step2Msg">Un code à 6 chiffres a été envoyé à <strong id="sentTo"></strong></p>
      <input id="codeInput" type="text" maxlength="6" placeholder="000000" inputmode="numeric">
      <div class="modal-feedback" id="fb2"></div>
      <button class="modal-btn" id="verify-code-btn" onclick="verifyCode()">✅ Vérifier le code</button>
      <button class="modal-btn secondary" id="back-step1-btn" onclick="goStep(1)">← Retour</button>

    </div>

    <!-- Étape 3 : nouveau mot de passe -->
    <div class="modal-step" id="step3">
      <p>Code vérifié ✅ Entrez votre nouveau mot de passe.</p>
      <div class="input-wrap" style="margin:0;letter-spacing:normal">
        <input id="newPwd" type="password" placeholder="Nouveau mot de passe" style="letter-spacing:normal;font-size:.9rem;font-weight:400">
      </div>
      <div class="input-wrap" style="margin:0;letter-spacing:normal">
        <input id="confirmPwd" type="password" placeholder="Confirmer le mot de passe" style="letter-spacing:normal;font-size:.9rem;font-weight:400">
      </div>
      <div class="modal-feedback" id="fb3"></div>
      <button class="modal-btn" id="reset-pwd-btn" onclick="resetPassword()">💾 Enregistrer</button>

    </div>

    <!-- Étape 4 : succès -->
    <div class="modal-step" id="step4">
      <p style="font-size:1.8rem;text-align:center">✅</p>
      <p>Votre mot de passe a été réinitialisé avec succès !</p>
      <button class="modal-btn" id="close-modal-success-btn" onclick="closeModal()">Retour à la connexion</button>

    </div>
  </div>
</div>

<script>
  // Pont de navigation intégré
  if (!window.hasAgroSmartBridge) {{
      window.hasAgroSmartBridge = true;
      window.addEventListener('message', function(event) {{
          if (event.data && event.data.type === 'navigate') {{
              window.location.href = event.data.url;
          }}
      }});
  }}


  window.addEventListener('load', () => {{
    if (LOGIN_ERROR) {{
      const fb = document.getElementById('feedback');
      fb.style.color = '#f08080';
      fb.textContent = LOGIN_ERROR;
    }}
  }});

  // Écoute des retours AJAX
  window.addEventListener('message', function(e) {{
      if (e.data.type === 'forgot_result') {{
          document.getElementById('send-code-btn').disabled = false;
          const fb = document.getElementById('fb1');
          if (e.data.success) {{
              const email = document.getElementById('resetEmail').value.trim();
              document.getElementById('sentTo').textContent = email;
              goStep(2);
          }} else {{
              fb.style.color = '#f08080'; fb.textContent = e.data.msg;
          }}
      }}
      if (e.data.type === 'verify_result') {{
          document.getElementById('verify-code-btn').disabled = false;
          const fb = document.getElementById('fb2');
          if (e.data.success) {{
              goStep(3);
          }} else {{
              fb.style.color = '#f08080'; fb.textContent = e.data.msg;
          }}
      }}
      if (e.data.type === 'reset_result') {{
          document.getElementById('reset-pwd-btn').disabled = false;
          const fb = document.getElementById('fb3');
          if (e.data.success) {{
              goStep(4);
          }} else {{
              fb.style.color = '#f08080'; fb.textContent = e.data.msg;
          }}
      }}
  }});

  function togglePwd() {{
    const p = document.getElementById('password');
    p.type = p.type === 'password' ? 'text' : 'password';
  }}

  async function handleLogin() {{
    const email = document.getElementById('email').value.trim();
    const pwd   = document.getElementById('password').value;
    const fb    = document.getElementById('feedback');
    if (!email || !pwd) {{
      fb.style.color = '#f08080'; fb.textContent = 'Veuillez remplir tous les champs.'; return;
    }}
    fb.style.color = '#a4b4ab'; fb.textContent = 'Vérification en cours...';
    
    try {{
      const res = await fetch('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ email: email, password: pwd, returnSecureToken: true }})
      }});
      const data = await res.json();
      
      if (data.localId) {{
        fb.style.color = '#7ed997'; fb.textContent = 'Connexion réussie ! Redirection...';
        const url = '/Connexion?action=login_success&uid=' + encodeURIComponent(data.localId);
        window.postMessage({{type: 'navigate', url: url}}, '*');
      }} else {{
        let err_msg = data.error && data.error.message ? data.error.message : "Erreur inconnue";
        if (err_msg.includes("INVALID_LOGIN_CREDENTIALS") || err_msg.includes("EMAIL_NOT_FOUND") || err_msg.includes("INVALID_PASSWORD")) {{
            err_msg = "Email ou mot de passe incorrect.";
        }} else if (err_msg.includes("USER_DISABLED")) {{
            err_msg = "Ce compte a été désactivé.";
        }} else if (err_msg.includes("TOO_MANY_ATTEMPTS_TRY_LATER")) {{
            err_msg = "Trop de tentatives. Réessayez plus tard.";
        }}
        fb.style.color = '#f08080'; fb.textContent = err_msg;
      }}
    }} catch (e) {{
      fb.style.color = '#f08080'; fb.textContent = 'Erreur réseau.';
    }}
  }}

  function openForgot() {{
    document.getElementById('modalBackdrop').classList.add('open');
    goStep(1);
  }}

  function closeModal() {{
    document.getElementById('modalBackdrop').classList.remove('open');
  }}
  function goStep(n) {{
    document.querySelectorAll('.modal-step').forEach(s => s.classList.remove('active'));
    document.getElementById('step' + n).classList.add('active');
  }}

  function callAjax(action, params) {{
    const iframe = document.createElement('iframe');
    let url = new URL(window.parent.location.origin + window.parent.location.pathname);
    url.searchParams.set('action', action);
    for (const key in params) {{
        url.searchParams.set(key, params[key]);
    }}
    iframe.src = url.toString();
    iframe.style.width = '1px';
    iframe.style.height = '1px';
    iframe.style.position = 'absolute';
    iframe.style.visibility = 'hidden';
    iframe.style.border = 'none';
    document.body.appendChild(iframe);
    
    // Nettoyage après 20 secondes
    setTimeout(() => iframe.remove(), 20000);
  }}

  function sendCode() {{
    const email = document.getElementById('resetEmail').value.trim();
    const fb    = document.getElementById('fb1');
    const btn   = document.getElementById('send-code-btn');
    if (!email || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) {{
      fb.style.color='#f08080'; fb.textContent='Email invalide.'; return;
    }}
    fb.style.color='#7ed997'; fb.textContent='Envoi en cours… Veuillez patienter.';
    btn.disabled = true;
    callAjax('forgot_ajax', {{ email: email }});
  }}

  function verifyCode() {{
    const code = document.getElementById('codeInput').value.trim();
    const email = document.getElementById('resetEmail').value.trim();
    const fb   = document.getElementById('fb2');
    const btn  = document.getElementById('verify-code-btn');
    if (code.length !== 6) {{
      fb.style.color='#f08080'; fb.textContent='Entrez le code à 6 chiffres.'; return;
    }}
    fb.style.color='#7ed997'; fb.textContent='Vérification…';
    btn.disabled = true;
    callAjax('verify_ajax', {{ code: code, email: email }});
  }}

  function resetPassword() {{
    const p1 = document.getElementById('newPwd').value;
    const p2 = document.getElementById('confirmPwd').value;
    const email = document.getElementById('resetEmail').value.trim();
    const code = document.getElementById('codeInput').value.trim();
    const fb = document.getElementById('fb3');
    const btn = document.getElementById('reset-pwd-btn');
    if (p1.length < 6) {{ fb.style.color='#f08080'; fb.textContent='Minimum 6 caractères.'; return; }}
    if (p1 !== p2)     {{ fb.style.color='#f08080'; fb.textContent='Les mots de passe ne correspondent pas.'; return; }}
    
    fb.style.color='#7ed997'; fb.textContent='Mise à jour en cours…';
    if (btn) btn.disabled = true;
    callAjax('reset_ajax', {{ pwd: p1, email: email, code: code }});
  }}
</script>

</body>
</html>
"""

st.components.v1.html(html_code, height=700, scrolling=False)
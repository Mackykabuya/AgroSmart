import streamlit as st
import base64, os
import firebase_admin
from firebase_admin import credentials, auth, firestore

if not firebase_admin._apps:
    base_path = os.path.dirname(os.path.dirname(__file__))
    key_path = os.path.join(base_path, "serviceAccountKey.json")
    if os.path.exists(key_path):
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)

db = firestore.client()
st.set_page_config(page_title="AgroSmart – Inscription", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    #MainMenu, header, footer { visibility: hidden !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    .block-container { padding: 0 !important; margin: 0 !important; max-width: 100vw !important; }
    .stApp { background: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# (Le pont de navigation est intégré dans le bloc HTML plus bas)

action = st.query_params.get("action", "")
if action == "register":
    nom = st.query_params.get("nom", ""); prenom = st.query_params.get("prenom", "")
    sexe = st.query_params.get("sexe", ""); tel = st.query_params.get("tel", "")
    email = st.query_params.get("email", ""); pwd = st.query_params.get("password", "")
    if email and pwd:
        try:
            user = auth.create_user(email=email, password=pwd)
            db.collection("users").document(user.uid).set({"nom":nom,"prenom":prenom,"sexe":sexe,"tel":tel,"email":email,"created_at":firestore.SERVER_TIMESTAMP})
            st.session_state["reg_success"] = "Compte créé avec succès ! Connectez-vous maintenant."
            st.query_params.clear()
            st.switch_page("pages/Connexion.py")
        except Exception as e: st.session_state["reg_error"] = str(e)
    st.query_params.clear(); st.rerun()

# Pas de redirection automatique — l'utilisateur doit se connecter manuellement
reg_error = st.session_state.get("reg_error", "")

# ── Image blob (Optimisée avec cache) ──
@st.cache_data
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
    return ""

bg_src = get_base64_image("farm_bg.jpg")
bg_url = f'url("{bg_src}")' if bg_src else 'url("https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=900&q=80")'

html_code = f"""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
#MainMenu, header, footer {{ visibility: hidden !important; }}
[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="collapsedControl"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; margin: 0 !important; max-width: 100vw !important; }}
.stApp {{ background: #ffffff !important; }}
.agro-wrapper {{ font-family:'Poppins',sans-serif; display:flex; align-items:center; justify-content:center; min-height:100vh; background:#ffffff; padding:20px; }}
.agro-card {{ display:flex; width:900px; min-height:600px; border-radius:24px; overflow:hidden; box-shadow:0 24px 64px rgba(0,0,0,.15); position:relative; }}
.agro-left {{ flex:1.2; position:relative; background:#e8f0e8; overflow:hidden; display:flex; align-items:center; justify-content:center; }}
.agro-bubble {{ position:absolute; border-radius:50%; background:rgba(255,255,255,.5); backdrop-filter:blur(4px); }}
.b1 {{ width:120px; height:120px; top:-40px; left:-40px; }}
.b2 {{ width:80px; height:80px; top:40px; right:40px; opacity:0.6; }}
.agro-blob {{ width:85%; height:85%; background-image:{bg_url}; background-size:cover; background-position:center; border-radius:40% 60% 50% 50%/50% 50% 60% 40%; animation:morph 8s infinite alternate; }}
@keyframes morph {{ 0% {{ border-radius:40% 60% 50% 50%/50% 50% 60% 40%; }} 100% {{ border-radius:60% 40% 60% 40%/40% 60% 40% 60%; }} }}
.agro-right {{ width:420px; background:#1a4a35; padding:35px; display:flex; flex-direction:column; justify-content:center; gap:12px; color:white; }}
.agro-right h1 {{ text-align:center; font-size:1.8rem; margin-bottom:5px; font-weight:700; }}
.agro-row {{ display:flex; gap:12px; }}
.agro-field {{ display:flex; flex-direction:column; gap:4px; flex:1; }}
.agro-field label {{ font-size:0.75rem; color:#d4e8d6; }}
.input-wrap {{ position:relative; display:flex; align-items:center; }}
.agro-input {{ width:100%; padding:10px 15px 10px 35px; background:#e8f5eb; border:none; border-radius:8px; color:#1a3a28; outline:none; font-family:inherit; font-size:0.85rem; }}
.agro-input:focus {{ box-shadow:0 0 0 3px #5cb87a; }}
.icon-left {{ position:absolute; left:10px; color:#5a8a6a; display:flex; align-items:center; pointer-events:none; }}
.icon-right {{ position:absolute; right:10px; color:#5a8a6a; cursor:pointer; display:flex; align-items:center; }}
.agro-btn {{ width:100%; padding:13px; background:#e8f5eb; color:#1a4a35; border:none; border-radius:10px; font-weight:700; cursor:pointer; transition:0.2s; margin-top:5px; }}
.agro-btn:hover {{ background:#c8eacc; transform:translateY(-1px); }}
.agro-footer {{ text-align:center; font-size:0.75rem; color:#9dbfa4; margin-top:5px; }}
.agro-footer a {{ color:#d4e8d6; text-decoration:underline; font-weight:600; cursor:pointer; }}
.agro-feedback {{ text-align:center; font-size:0.75rem; color:#f08080; min-height:16px; }}
</style>
<div class="agro-wrapper">
<div class="agro-card">
<div class="agro-left"><div class="agro-bubble b1"></div><div class="agro-bubble b2"></div><div class="agro-blob"></div></div>
<div class="agro-right">
<h1>Inscription</h1>
<div class="agro-row">
<div class="agro-field"><label>Nom</label><div class="input-wrap"><span class="icon-left"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg></span><input type="text" id="nom" class="agro-input" placeholder="Nom" required></div></div>
<div class="agro-field"><label>Prénom</label><div class="input-wrap"><span class="icon-left"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg></span><input type="text" id="prenom" class="agro-input" placeholder="Prénom" required></div></div>
</div>
<div class="agro-row">
<div class="agro-field"><label>Sexe</label><div class="input-wrap"><span class="icon-left"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg></span><select id="sexe" class="agro-input" style="appearance:none;" required><option value="">--</option><option value="homme">Homme</option><option value="femme">Femme</option></select></div></div>
<div class="agro-field"><label>Téléphone</label><div class="input-wrap"><span class="icon-left"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M6.62 10.79c1.44 2.83 3.76 5.15 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg></span><input type="tel" id="tel" class="agro-input" placeholder="+213..." required></div></div>
</div>
<div class="agro-field"><label>Email</label><div class="input-wrap"><span class="icon-left"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg></span><input type="email" id="email" class="agro-input" placeholder="exemple@mail.com" required></div></div>
<div class="agro-field"><label>Mot de passe</label><div class="input-wrap"><span class="icon-left"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm3 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/></svg></span><input type="password" id="pwd" class="agro-input" placeholder="••••••••" required><span class="icon-right" onclick="toggleVis('pwd')"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg></span></div></div>
<div class="agro-field"><label>Confirmer</label><div class="input-wrap"><span class="icon-left"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm3 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/></svg></span><input type="password" id="conf" class="agro-input" placeholder="••••••••" required><span class="icon-right" onclick="toggleVis('conf')"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg></span></div></div>
<button class="agro-btn" id="reg-btn" onclick="handleReg()">S'inscrire</button>
<div id="fb" class="agro-feedback"></div>
<p class="agro-footer">Déjà un compte ? <a href="/Connexion">Connectez-vous</a></p>
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

function toggleVis(id){{
    const i = document.getElementById(id);
    i.type = i.type === 'password' ? 'text' : 'password';
}}

function handleReg(){{
    const n = document.getElementById('nom').value;
    const p = document.getElementById('prenom').value;
    const s = document.getElementById('sexe').value;
    const t = document.getElementById('tel').value;
    const e = document.getElementById('email').value;
    const w = document.getElementById('pwd').value;
    const c = document.getElementById('conf').value;
    const fb = document.getElementById('fb');
    
    if(!n||!p||!e||!w||!c){{fb.textContent="Tous les champs sont requis"; return;}}
    if(w!==c){{fb.textContent="Les mots de passe ne correspondent pas"; return;}}
    
    fb.style.color='#7ed997';
    fb.textContent='Inscription réussie ! Redirection...';
    
    const url = '/Inscription?action=register&nom='+encodeURIComponent(n)+'&prenom='+encodeURIComponent(p)+'&sexe='+encodeURIComponent(s)+'&tel='+encodeURIComponent(t)+'&email='+encodeURIComponent(e)+'&password='+encodeURIComponent(w);
    window.postMessage({{type: 'navigate', url: url}}, '*');
}}

// Affichage de l'erreur au chargement
const regError = "{reg_error}";
if (regError) {{
    const fb = document.getElementById('fb');
    if (fb) {{
        fb.textContent = regError;
        fb.style.color = '#f08080';
    }}
}}
</script>
"""
st.components.v1.html(html_code, height=680, scrolling=False)
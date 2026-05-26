import streamlit as st
import json

# 1. Configuration
st.set_page_config(page_title="AgroSmart", layout="wide", initial_sidebar_state="collapsed")

if st.session_state.get("show_success"):
    st.toast(st.session_state["show_success"], icon="✅")
    del st.session_state["show_success"]

# Gestion Déconnexion
if st.query_params.get("action") == "logout":
    st.session_state["user"] = None
    st.query_params.clear()
    st.rerun()

# 2. Masquage des éléments Streamlit
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden !important;}
        [data-testid="stSidebar"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}
        .stApp {bottom: 0px;}
        .block-container {padding: 0px !important; max-width: 100% !important;}
    </style>
""", unsafe_allow_html=True)

# 3. Cinq images professionnelles de très haute qualité
bg_images = [
    "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1600&q=80"
]

bg_images_json = json.dumps(bg_images)

# Définition des boutons selon l'état de connexion
if not st.session_state.get("user"):
    buttons_html = """
    <a href="/Connexion" target="_self" class="btn-link btn-login">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline; margin-right:6px;">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
        Se connecter
    </a>
    <a href="/Inscription" target="_self" class="btn-link btn-signup">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline; margin-right:6px;">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
            <line x1="12" y1="12" x2="12" y2="18"/>
            <line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        Créer un compte
    </a>
    """
else:
    buttons_html = """
    <a href="/Tableau_de_bord" target="_self" class="btn-link btn-login">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline; margin-right:6px;">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        Tableau de bord
    </a>
    <a href="/?action=logout" target="_self" class="btn-link btn-signup" style="background: rgba(220, 53, 69, 0.6);">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline; margin-right:6px;">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        Déconnexion
    </a>
    """

# 4. Design final
design_final = f"""
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100%; font-family: 'Poppins', sans-serif; overflow: auto; }}
        
        .slideshow-container {{
            position: relative;
            height: 100vh;
            width: 100%;
            overflow: hidden;
        }}
        
        .slide {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            opacity: 0;
            transition: opacity 1.5s ease-in-out;
            z-index: 1;
        }}
        
        .slide.active {{
            opacity: 1;
            z-index: 2;
        }}
        
        .overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(rgba(0,0,0,0.35), rgba(0,0,0,0.35));
            z-index: 3;
            pointer-events: none;
        }}
        
        .card-wrapper {{
            position: relative;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            width: 100%;
        }}

        @keyframes floatCard {{
            0% {{ transform: translateY(20px); opacity: 0; }}
            100% {{ transform: translateY(0); opacity: 1; }}
        }}

        @keyframes floatIcon {{
            0%, 100% {{ transform: translateX(-50%) translateY(-32px); }}
            50% {{ transform: translateX(-50%) translateY(-42px); }}
        }}

        .card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 45px;
            padding: 55px 40px 40px;
            width: 440px;
            text-align: center;
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            position: relative;
            opacity: 0;
            transform: translateY(20px);
            animation: floatCard 1.2s ease-out forwards;
        }}

        .icon-top {{
            background: #7ed997;
            width: 65px; height: 65px;
            border-radius: 18px;
            position: absolute;
            top: -32px; left: 50%;
            transform: translateX(-50%);
            display: flex; align-items: center; justify-content: center;
            font-size: 32px;
            animation: floatIcon 3.5s ease-in-out infinite;
            color: #1a4a35;
        }}

        h1 {{ font-size: 3.2rem; font-weight: 800; margin: 10px 0 0; letter-spacing: -2px; }}
        .green {{ color: #7ed997; }}
        .sub {{ font-size: 0.85rem; opacity: 0.9; margin: 10px 0 25px; line-height: 1.4; }}

        .badges {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 30px; }}
        .badge {{ 
            background: rgba(255,255,255,0.15); 
            padding: 6px 14px; border-radius: 20px; 
            font-size: 0.7rem; border: 1px solid rgba(255,255,255,0.1); 
        }}

        .btn-link {{
            display: block;
            width: 90%;
            margin: 12px auto;
            padding: 15px;
            border-radius: 20px;
            font-size: 1.1rem;
            font-weight: 600;
            text-decoration: none;
            color: white;
            border: 2px solid white;
            transition: 0.3s, box-shadow 0.3s;
            text-align: center;
        }}

        .btn-login {{ background: #2d7a4f; }}
        .btn-signup {{ background: rgba(139, 115, 85, 0.45); }}
        .btn-link:hover {{
            transform: scale(1.04);
            opacity: 0.95;
            box-shadow: 0 14px 22px rgba(0,0,0,0.2);
        }}
        
        .footer-text {{ font-size: 0.65rem; opacity: 0.6; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="slideshow-container" id="slideshow-container">
        <div class="overlay"></div>
        <div class="card-wrapper">
            <div class="card">
                <div class="icon-top">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2c.5 0 1 .5 1 1v4c0 .5-.5 1-1 1s-1-.5-1-1V3c0-.5.5-1 1-1z"/>
                        <path d="M12 10c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
                        <path d="M12 8c-2.2 0-4 1.8-4 4s1.8 4 4 4 4-1.8 4-4-1.8-4-4-4z"/>
                        <path d="M6 14c-2.2 0-4 1.8-4 4s1.8 4 4 4 4-1.8 4-4-1.8-4-4-4z"/>
                        <path d="M18 14c-2.2 0-4 1.8-4 4s1.8 4 4 4 4-1.8 4-4-1.8-4-4-4z"/>
                    </svg>
                </div>
                <h1>Agro<span class="green">Smart</span></h1>
                <p class="sub">Système intelligent d'optimisation de l'irrigation et de diagnostic pédologique basé sur l'IA & IoT</p>
                
                <div class="badges">
                    <div class="badge">Capteurs IoT</div>
                    <div class="badge">Machine Learning</div>
                    <div class="badge">Irrigation</div>
                    <div class="badge">Diagnostic Sol</div>
                </div>

                {buttons_html}
                
                <div class="footer-text">©2026 AgroSmart</div>
            </div>
        </div>
    </div>

    <script>
        const images = {bg_images_json};
        const container = document.getElementById('slideshow-container');
        
        images.forEach((img, index) => {{
            const slide = document.createElement('div');
            slide.className = 'slide';
            slide.style.backgroundImage = `url("${{img}}")`;
            slide.setAttribute('data-index', index);
            if (index === 0) slide.classList.add('active');
            container.insertBefore(slide, container.firstChild);
        }});
        
        let current = 0;
        let slides = document.querySelectorAll('.slide');
        const total = slides.length;
        
        function showSlide(index) {{
            slides.forEach((slide, i) => {{
                if (i === index) slide.classList.add('active');
                else slide.classList.remove('active');
            }});
        }}
        
        function nextSlide() {{
            current = (current + 1) % total;
            showSlide(current);
        }}
        
        setInterval(nextSlide, 5000);
    </script>
</body>
</html>
"""

st.components.v1.html(design_final, height=700, scrolling=False)
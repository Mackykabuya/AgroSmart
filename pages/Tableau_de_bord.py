import streamlit as st
import base64, os
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# 1. Actualisation automatique (10 secondes)
st_autorefresh(interval=10000, key="datarefresh")

# 2. Configuration de la page
st.set_page_config(page_title="AgroSmart - Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Initialisation Firebase
if not firebase_admin._apps:
    base_path = os.path.dirname(os.path.dirname(__file__))
    key_path = os.path.join(base_path, "serviceAccountKey.json")
    if os.path.exists(key_path):
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)

db = firestore.client()

# 3. Vérification de la connexion
if not st.session_state.get("user"):
    st.warning("Veuillez vous connecter pour accéder au tableau de bord.")
    st.switch_page("pages/Connexion.py")
    st.stop()

user_id = st.session_state.get("user")

# --- LE PONT DYNAMIQUE ---
# On dit au simulateur : "Hé, c'est cet ID qui regarde le dashboard maintenant !"
db.collection("config").document("simulator").set({"active_user_id": user_id})
# -------------------------

# 4. Récupération des données
user_name = "Agriculteur"
user_initial = "A"
current_temp, current_hum, current_ph = "--", "--", "--"
df = pd.DataFrame()

try:
    # A. Infos de l'utilisateur
    u_doc = db.collection("users").document(user_id).get()
    if u_doc.exists:
        u_data = u_doc.to_dict()
        user_name = u_data.get("prenom", "Agriculteur").capitalize()
        user_initial = user_name[0].upper()

    # B. Données capteurs
    query = db.collection("users").document(user_id).collection("donnees_capteurs") \
              .order_by("timestamp", direction="DESCENDING").limit(30).get()
    
    if query:
        data_list = [d.to_dict() for d in query]
        df = pd.DataFrame(data_list)
        col_temp = "temperature" if "temperature" in df.columns else ("temp" if "temp" in df.columns else None)
        col_hum = "humidite" if "humidite" in df.columns else ("humidity" if "humidity" in df.columns else None)
        col_ph = "ph"
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values("timestamp")

        latest = df.iloc[-1]
        current_temp = f"{latest[col_temp]} °C" if col_temp else "Erreur"
        current_hum = f"{latest[col_hum]} %" if col_hum else "Erreur"
        current_ph = f"{latest[col_ph]}" if col_ph in latest else "--"

except Exception as e:
    st.error(f"Erreur de synchronisation : {e}")

# 5. CSS & HTML
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden !important;}
        [data-testid="stSidebar"] {display: none !important;}
        .stApp {background-color: #0f1a14;}
    </style>
""", unsafe_allow_html=True)

html_dashboard = f"""
<div style="font-family: 'Poppins', sans-serif; color: white;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h1 style="font-size: 1.8rem; color: #7ed997;">Bonjour, {user_name} 👋</h1>
        <div style="background: rgba(255,255,255,0.05); padding: 5px 15px; border-radius: 20px; display: flex; align-items: center; gap: 10px;">
            <div style="width: 30px; height: 30px; background: #7ed997; border-radius: 50%; color: #0f1a14; display: flex; align-items: center; justify-content: center; font-weight: bold;">{user_initial}</div>
            <span>{user_name}</span>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(126, 217, 151, 0.2); border-radius: 15px; padding: 20px; text-align: center;">
            <span style="color:#a4b4ab;">🌡️ Température</span>
            <div style="font-size: 1.5rem; font-weight: bold; color: #7ed997;">{current_temp}</div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(126, 217, 151, 0.2); border-radius: 15px; padding: 20px; text-align: center;">
            <span style="color:#a4b4ab;">💧 Humidité</span>
            <div style="font-size: 1.5rem; font-weight: bold; color: #7ed997;">{current_hum}</div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(126, 217, 151, 0.2); border-radius: 15px; padding: 20px; text-align: center;">
            <span style="color:#a4b4ab;">🧪 pH Sol</span>
            <div style="font-size: 1.5rem; font-weight: bold; color: #7ed997;">{current_ph}</div>
        </div>
    </div>
</div>
"""
st.components.v1.html(html_dashboard, height=200)

# 6. Graphique
if not df.empty:
    st.write("---")
    st.subheader("📈 Évolution des paramètres")
    fig = px.line(df, x="timestamp", y=[c for c in [col_temp, col_hum] if c], 
                  template="plotly_dark", color_discrete_sequence=["#7ed997", "#3d85c6"])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Lancez le simulateur pour voir les graphiques.")
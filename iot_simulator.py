import firebase_admin
from firebase_admin import credentials, firestore
import random
import time
from datetime import datetime

# 1. Configuration
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Simulateur prêt et connecté.")
except Exception as e:
    print(f"❌ Erreur : {e}")

def executer_simulation():
    print("🚀 Attente d'un utilisateur sur le Dashboard...")
    
    try:
        while True:
            # Récupération automatique de l'utilisateur qui navigue sur le site
            config_doc = db.collection("config").document("simulator").get()
            
            if config_doc.exists:
                user_id = config_doc.to_dict().get("active_user_id")
                
                if user_id:
                    donnees = {
                        "timestamp": datetime.now(),
                        "ph": round(random.uniform(5.5, 7.8), 2),
                        "humidite": round(random.uniform(20.0, 65.0), 2),
                        "temperature": round(random.uniform(24.0, 32.0), 2),
                        "unite": "Celsius"
                    }

                    # Envoi au bon utilisateur
                    db.collection("users").document(user_id).collection("donnees_capteurs").add(donnees)
                    
                    print(f"📡 [OK] Données envoyées vers {user_id[:8]}... | Temp: {donnees['temperature']}°C")
                else:
                    print("⏳ Aucun utilisateur n'est actuellement sur le Dashboard.")
            else:
                print("⏳ En attente de signal du Dashboard (connectez-vous)...")

            time.sleep(10)

    except KeyboardInterrupt:
        print("\n⏹️ Simulation stoppée.")

if __name__ == "__main__":
    executer_simulation()
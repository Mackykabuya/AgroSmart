# ══════════════════════════════════════════════════════
#  config.py — Configuration email pour AgroSmart
#  Réinitialisation mot de passe via Gmail SMTP
# ══════════════════════════════════════════════════════
#
#  ÉTAPES pour activer l'envoi réel d'emails :
#
#  1. Connectez-vous à votre compte Gmail
#  2. Allez sur : https://myaccount.google.com/security
#  3. Activez la "Validation en deux étapes" si ce n'est pas fait
#  4. Cherchez "Mots de passe des applications"
#  5. Créez un mot de passe pour "Autre (nom personnalisé)" → "AgroSmart"
#  6. Copiez le mot de passe à 16 caractères généré
#  7. Collez-le dans EMAIL_PASSWORD ci-dessous
#
# ══════════════════════════════════════════════════════

EMAIL_ADDRESS  = "fistonsalimia13@gmail.com"   # ← Votre adresse Gmail
EMAIL_PASSWORD = "fjgp fsom jwnz ohtk"     # ← Mot de passe d'application Gmail (16 car.)

SMTP_SERVER    = "smtp.gmail.com"
SMTP_PORT      = 587

# Durée de validité du code (en minutes)
CODE_EXPIRY_MINUTES = 10

# Clé API Web Firebase pour l'authentification
FIREBASE_WEB_API_KEY = "AIzaSyBE6BT71J2gyyX-QcO_PBQfFCK2XbdErms"

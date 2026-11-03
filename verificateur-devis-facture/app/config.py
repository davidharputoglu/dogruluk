"""Configuration de l'application Verificateur Devis-Facture.

Le nom / branding de l'application se change en UNE SEULE PLACE :
la variable APP_NAME ci-dessous (ou la variable d'environnement VDF_APP_NAME).

Deux editions sont prevues (choix utilisateur) :
  - edition publique  -> nom public   (defaut : "VerifFact")
  - edition privee    -> nom prive    (defaut : "VerifFact Pro")
La distinction se fait par la variable d'environnement VDF_EDITION = public|prive.
L'edition privee active des fonctions supplementaires (import mail, dossier surveille,
export PDF des ecarts) qui restent desactivees en version publique en v0.1.
"""
from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Branding - changer cette ligne pour renommer l'application partout
# ---------------------------------------------------------------------------
EDITION = os.environ.get("VDF_EDITION", "public").lower()

if EDITION == "prive":
    APP_NAME = os.environ.get("VDF_APP_NAME", "VerifFact Pro")
    APP_TAGLINE = "Verification devis & factures tous fournisseurs - edition privee"
else:
    APP_NAME = os.environ.get("VDF_APP_NAME", "VerifFact")
    APP_TAGLINE = "Verification devis & factures tous fournisseurs"

FEATURE_EMAIL_IMPORT = EDITION == "prive"      # a ajouter plus tard (boite mail dediee)
FEATURE_WATCHED_FOLDER = EDITION == "prive"    # a ajouter plus tard (dossier surveille)
FEATURE_PDF_EXPORT = True                      # export PDF des ecarts

VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Crédits / contact (modifiables via variables d'environnement)
# ---------------------------------------------------------------------------
AUTHOR_NAME = os.environ.get("VDF_AUTHOR_NAME", "David HARPUTOGLU")
AUTHOR_EMAIL = os.environ.get("VDF_AUTHOR_EMAIL", "kasparof57@gmail.com")
AUTHOR_CREDIT = f"{AUTHOR_NAME} — aidé par IA"

# Base SQLite (fichier unique, compatible Raspberry Pi 3 ARM/ARM64)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("VDF_DATA_DIR", os.path.join(BASE_DIR, "data"))
EXPORT_DIR = os.environ.get("VDF_EXPORT_DIR", os.path.join(BASE_DIR, "exports"))
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "verif.db")

# Marge de tolerance pour les arrondis (euros), modifiable par fournisseur
DEFAULT_TOLERANCE = float(os.environ.get("VDF_TOLERANCE", "0.01"))

HOST = os.environ.get("VDF_HOST", "0.0.0.0")
PORT = int(os.environ.get("VDF_PORT", "8000"))

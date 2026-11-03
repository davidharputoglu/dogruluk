# VerifFact — Vérificateur de devis & factures (v0.1)

Application autonome qui vérifie les factures/devis de **tous fournisseurs**
(Point.P, etc.) par rapport à une **liste de prix négociés**, calcule les
**écarts** et fait le **récapitulatif des achats par chantier**.

## Règles implémentées (issues des 2 audios WhatsApp)

1. **Liste de prix de référence** : on importe la liste de prix du fournisseur ;
   elle sert de base de comparaison.
2. **Vérification ligne à ligne** de chaque facture importée :
   `écart = (prix facturé − prix convenu) × quantité`, cumulé par ligne,
   par facture et au total.
3. **Articles sans prix connu** : mis à part avec le message
   *« je n'ai pas le prix de ça »*. On peut compléter la liste directement
   dans l'app → la facture est re-vérifiée automatiquement.
4. **Rapprochement intelligent** : d'abord par **code article**, puis par
   **désignation** (normalisée, insensible à la casse/accents/ponctuation).
5. **Tolérance d'arrondi** paramétrable par fournisseur (défaut : 0,01 €).
6. **Récapitulatif par chantier** : chaque facture porte un nom de chantier ;
   l'app agrège les achats, totaux et écarts par chantier.

## Formats d'import acceptés (v0.1)

| Format | Statut |
|---|---|
| Excel (.xlsx) / CSV | ✅ |
| Facture électronique **Factur-X (PDF/XML)**, **UBL**, **CII** | ✅ (obligation e-invoicing FR dès 09/2026) |
| PDF simple (texte extractible) | ✅ basique |
| Scan / photo (OCR) | 🔜 v0.2 |
| Boîte mail dédiée / dossier surveillé | 🔜 v0.2 (édition privée) |

## Export

- **Excel / CSV des écarts** par facture ou par chantier → à envoyer au
  fournisseur pour demander un **avoir**.

## Deux éditions (une seule ligne à changer)

Le nom/appearance se règlent dans `app/config.py` (ou variables d'env) :

- Édition **publique** : `VDF_APP_NAME=VerifPublique`
- Édition **privée** : `VDF_APP_NAME=VerifPrivee` + fonctionnalités avancées
  (imports mail/dossier surveillé à venir).

Autres variables : `VDF_DATA_DIR`, `VDF_EXPORT_DIR`, `VDF_TOLERANCE`.

## Lancer l'application

### Windows (double-clic / cmd)
```bat
py -3.12 -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
:: puis ouvrir http://localhost:8000
```

### Linux / Raspberry Pi 3 (ARM & ARM64)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./scripts/run.sh            # ou : python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Aucune dépendance lourde : SQLite + Python pur → OK sur RPi 3 (1 Go RAM).

### Docker / Podman / Portainer (multi-arch amd64 + arm64)
```bash
docker buildx create --use                       # une fois
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t veriffact:0.1 --push .                      # image pour PC et RPi
# ou en local simple :
docker compose up -d     # http://localhost:8000
podman compose up -d     # idem (Portainer : importer docker-compose.yml)
```

## Tests

```bash
python tests/test_verification.py        # sans pytest
python -m pytest tests -q                # avec pytest
```

## Structure

```
app/
  main.py            # FastAPI + pages web (dashboard, chantiers, factures…)
  config.py          # noms des éditions, tolérance, dossiers données
  db.py              # SQLite (fournisseurs, prix, factures, lignes, chantiers)
  parsers/           # excel_csv, einvoice (Factur-X/UBL/CII), pdf_simple
  services/          # importing, verification (moteur d'écarts), exporting
samples/             # exemples CSV liste de prix + facture
scripts/             # run.sh, make_samples.py
tests/               # test_verification.py (règles des 2 audios + UBL)
```

## Prochaines étapes (v0.2)

- OCR scan/photo (rapport d'import par lots, à valider avant enregistrement).
- Export PDF « demande d'avoir ».
- Édition privée : relèvement automatique d'une boîte mail + dossier surveillé.
- Calibration du parseur PDF sur vos **vraies** factures Point.P
  (déposer 1–2 exemples dans `samples/`).

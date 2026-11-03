# Doğruluk — vérificateur de devis & factures, tous fournisseurs

**Version 0.1 (figée jusqu'à demande explicite de l'éditeur)**
**Éditeur : David HARPUTOGLU — aidé par IA · Contact : kasparof57@gmail.com**
**Dépôt public : https://github.com/davidharputoglu/dogruluk**

Doğruluk (« exactitude » en turc) contrôle ligne à ligne vos factures et devis
fournisseurs (Point.P ou tout autre fournisseur) contre vos listes de prix
négociées :

- écart = **(prix facturé − prix convenu) × quantité**, cumulé par ligne, par facture et au global ;
- articles absents de la liste mis de côté : *« je n'ai pas le prix de ça »* → complétez la liste, re-vérification automatique ;
- rapprochement d'abord **par code article**, puis par désignation ; tolérance d'arrondi configurable (globale et par fournisseur) ;
- **récapitulatif des achats par chantier** ;
- import **Excel / CSV, PDF, facture électronique (Factur-X, UBL, CII)** ;
- exports Excel/CSV des écarts (pour demander un avoir) et des totaux chantiers ;
- interface moderne multi-thèmes : **turquoise (défaut)**, sombre, noir, personnalisable ;
- 14 langues : français, arabe (RTL), anglais, italien, espagnol, portugais, turc, azéri, kazakh, kirghize, ouzbek, turkmène, tatar, bachkir ;
- mentions légales, politique de confidentialité et licence intégrées (pages `/mentions-legales`, `/confidentialite`, `/licence` + fichiers `LICENSE` / `NOTICE`).

## Démarrage rapide

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# http://localhost:8000
```

Windows : double-cliquez `scripts/run_windows.bat` (nécessite Python 3.10+).

## Installations disponibles (générées par GitHub Actions, tag `v*`)

Le workflow `.github/workflows/build.yml` construit automatiquement, pour chaque tag :

| Plateforme | Artefacts |
|---|---|
| **Windows** | installeur `dogruluk-0.1-setup.exe` (Inno Setup) + `dogruluk-0.1-windows-portable.zip` |
| **Linux** | paquets `.deb` (amd64/arm64/armhf), `.rpm`, AppImage, script `scripts/install.sh`, code source `.tar.gz` |
| **Docker / Portainer / Podman / NAS** | image multi-arch `ghcr.io/davidharputoglu/dogruluk:0.1` (amd64, arm/v7, arm64) + archives `.tar.gz` par architecture pour import hors-ligne (Synology, QNAP, TrueNAS, unRAID…) |
| **Raspberry Pi 3 (ARMv7) et ARM64** | via `.deb` armhf/arm64, `install.sh`, ou l'image Docker `linux/arm/v7` |

Installation express Linux/RPi :

```bash
sudo bash scripts/install.sh        # service systemd + port 8000
```

Docker (toutes plateformes, dont Portainer/Podman) :

```bash
docker run -d --name dogruluk -p 8000:8000 \
  -v dogruluk_data:/data -v dogruluk_exports:/exports \
  ghcr.io/davidharputoglu/dogruluk:0.1
```

Sans accès réseau : téléchargez `dogruluk_0.1_linux-<arch>.tar.gz` depuis la Release,
puis `docker load < dogruluk_0.1_linux-amd64.tar.gz` (fonctionne aussi avec Podman :
`podman load`).

## Réglages persistants (page « Paramètres »)

Nom affiché, langue, tolérance par défaut, devise, éditeur/contact — stockés dans
la base SQLite locale (`data/verif.db`), ils priment sur les variables
d'environnement. Le thème est mémorisé côté navigateur (localStorage + cookie).

Variables d'environnement techniques : `VDF_APP_NAME`, `VDF_VERSION`,
`VDF_EDITION`, `VDF_TOLERANCE`, `VDF_LANG`, `VDF_HOST`, `VDF_PORT`,
`VDF_DATA_DIR`, `VDF_EXPORT_DIR`, `VDF_AUTHOR_NAME`, `VDF_AUTHOR_EMAIL`.

## Tests

```bash
python -m pytest tests -q
```

## Licence & mentions légales

Voir `LICENSE` (Licence Doğruluk 1.0), `NOTICE`, et les pages intégrées.
Résumé : usage interne libre en conservant le crédit
« David HARPUTOGLU — aidé par IA » ; redistribution commerciale interdite sans
accord écrit ; calculs indicatifs, sans garantie de résultat ; logiciel 100 %
local, aucune donnée envoyée sur Internet, aucun cookie de suivi.
« Point.P » est une marque déposée de ses propriétaires ; ce projet n'est ni
affilié ni cautionné par Point.P ou tout autre fournisseur.

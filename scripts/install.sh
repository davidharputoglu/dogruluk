#!/usr/bin/env bash
# Doğruluk — installeur universel Linux (deb/rpm non requis) + Raspberry Pi 3+
# Usage : curl -fsSL https://raw.githubusercontent.com/davidharputoglu/dogruluk/main/scripts/install.sh | bash
#   ou  : ./install.sh
set -euo pipefail

APP="dogruluk"
REPO_URL="${DOGRULUK_REPO_URL:-https://github.com/davidharputoglu/dogruluk.git}"
TAG="${DOGRULUK_TAG:-v0.1}"          # version figée à 0.1 (décision éditeur)
INSTALL_DIR="/opt/${APP}"
DATA_DIR="/var/lib/${APP}"
PORT="${DOGRULUK_PORT:-8000}"

echo "== Doğruluk v${TAG} — installation =="

if [ "$(id -u)" -ne 0 ]; then
  echo "Lancez ce script en root (sudo ./install.sh)." >&2
  exit 1
fi

ARCH=$(uname -m)
echo "Architecture détectée : ${ARCH} (amd64/armv7l/aarch64 tous supportés)"

# --- dépendances -------------------------------------------------------------
if command -v apt-get >/dev/null 2>&1; then
  apt-get update -y
  apt-get install -y git python3 python3-venv python3-pip
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y git python3 python3-pip
elif command -v yum >/dev/null 2>&1; then
  yum install -y git python3 python3-pip
elif command -v zypper >/dev/null 2>&1; then
  zypper --non-interactive install git python3 python3-pip
else
  echo "Distrib non reconnue : installez Python >= 3.9 et git, puis relancez." >&2
  exit 1
fi

# --- code --------------------------------------------------------------------
if [ ! -d "$INSTALL_DIR" ]; then
  git clone --depth 1 --branch "$TAG" "$REPO_URL" "$INSTALL_DIR"
else
  git -C "$INSTALL_DIR" fetch --depth 1 origin "$TAG" && git -C "$INSTALL_DIR" reset --hard FETCH_HEAD
fi

python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --no-cache-dir -r "$INSTALL_DIR/requirements.txt"

mkdir -p "$DATA_DIR"

# --- service systemd ---------------------------------------------------------
cat > "/etc/systemd/system/${APP}.service" <<EOF
[Unit]
Description=Doğruluk — vérificateur de devis & factures (David HARPUTOGLU — aidé par IA)
After=network.target

[Service]
Environment=VDF_DATA_DIR=${DATA_DIR}
Environment=VDF_EXPORT_DIR=${DATA_DIR}/exports
Environment=VDF_HOST=0.0.0.0
Environment=VDF_PORT=${PORT}
Environment=VDF_EDITION=public
ExecStart=${INSTALL_DIR}/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
WorkingDirectory=${INSTALL_DIR}
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now "${APP}.service"

IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
echo ""
echo "✔ Doğruluk est installé et tourne sur http://${IP}:${PORT}"
echo "  Données : ${DATA_DIR}  (sauvegardez ce dossier)"
echo "  Mise à jour : sudo ./install.sh   |   Désinstallation : sudo ./install.sh --remove"

if [ "${1:-}" = "--remove" ]; then
  systemctl disable --now "${APP}.service" || true
  rm -f "/etc/systemd/system/${APP}.service"
  rm -rf "$INSTALL_DIR"
  echo "Désinstallé (vos données dans ${DATA_DIR} sont conservées ; supprimez-les si besoin)."
fi

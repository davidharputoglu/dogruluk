# Image unique multi-arch : linux/amd64 (PC Windows via WSL2/Docker Desktop,
# Linux), linux/arm/v7 (Raspberry Pi 3 - ARM), linux/arm64 (RPi 4/5, ARM64).
# Construire avec : docker buildx build --platform linux/amd64,linux/arm/v7,linux/arm64 -t veriffact .
FROM python:3.12-slim

WORKDIR /srv/app

# sqlite3 est dans la stdlib Python ; aucun paquet lourd -> image petite pour RPi3
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV VDF_HOST=0.0.0.0 VDF_PORT=8000 \
    VDF_DATA_DIR=/data VDF_EXPORT_DIR=/exports \
    VDF_EDITION=public VDF_APP_NAME=""

VOLUME ["/data", "/exports"]
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

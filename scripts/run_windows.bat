@echo off
rem ============================================================
rem  Dogruluk v0.1 - demarrage rapide Windows (version portable)
rem  Telechargez Python 3.10+ depuis https://python.org (cochez
rem  "Add python.exe to PATH"), puis double-cliquez sur ce fichier.
rem ============================================================
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo Installez-le depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [1/3] Creation de l'environnement virtuel...
    python -m venv .venv
)

echo [2/3] Installation des dependances...
".venv\Scripts\python" -m pip install --no-cache-dir -q -r requirements.txt

echo [3/3] Demarrage de Dogruluk (v0.1) - David HARPUTOGLU, aide par IA
echo Ouvrez http://localhost:8000 dans votre navigateur.
start "" http://localhost:8000
".venv\Scripts\python" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

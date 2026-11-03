@echo off
rem ============================================================
rem  Dogruluk v0.1 - demarrage (installe ou version portable)
rem  David HARPUTOGLU - aide par IA - kasparof57@gmail.com
rem ============================================================
cd /d "%~dp0"

set PY=python
where py >nul 2>nul && set PY=py
%PY% --version >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo Installez-le depuis https://www.python.org/downloads/
    echo ^(cochez "Add python.exe to PATH"^), puis relancez ce fichier.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [1/3] Creation de l'environnement virtuel...
    %PY% -m venv .venv
)

echo [2/3] Verification des dependances...
".venv\Scripts\python" -c "import uvicorn, fastapi" >nul 2>nul || \
  ".venv\Scripts\python" -m pip install --no-cache-dir -q -r requirements.txt

echo [3/3] Demarrage de Dogruluk v0.1 - http://localhost:8000
start "" http://localhost:8000
".venv\Scripts\python" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

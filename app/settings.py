"""Reglages persistes (SQLite) : nom appli, langue, tolerance defaut, devise,
editeur / mentions legales. Priment sur les variables d'environnement."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from .config import DATA_DIR, DB_PATH

DEFAULTS = {
    "app_name": "",             # vide => APP_NAME du .env / defaut
    "language": "",             # vide => VDF_LANG / fr
    "tolerance_default": "0.01",
    "currency": "EUR",
    "editor_name": "David HARPUTOGLU — aidé par IA",
    "editor_email": "kasparof57@gmail.com",
}


def _conn() -> sqlite3.Connection:
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS settings(
        key TEXT PRIMARY KEY, value TEXT NOT NULL)""")
    return c


def get(key: str) -> str:
    c = _conn()
    try:
        row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    finally:
        c.close()
    if row is not None and row[0] != "":
        return row[0]
    return DEFAULTS.get(key, "")


def all_settings() -> dict[str, str]:
    return {k: get(k) for k in DEFAULTS}


def set_many(values: dict[str, str]) -> None:
    c = _conn()
    try:
        for k, v in values.items():
            if k in DEFAULTS:
                c.execute(
                    "INSERT INTO settings(key,value) VALUES(?,?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (k, v))
        c.commit()
    finally:
        c.close()

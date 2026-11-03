"""Couche base de donnees SQLite (stdlib, aucune dependance externe).

Modele :
  suppliers        fournisseurs (Point.P et tous les autres)
  price_items      liste de prix de reference (prix negocies) par fournisseur
  sites            chantiers
  invoices         factures / devis importes
  invoice_lines    lignes facturees
  missing_items    articles absents de la liste de prix ("je n'ai pas le prix de ca")
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    tolerance REAL NOT NULL DEFAULT 0.01,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS price_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    code TEXT NOT NULL,                -- code article (ex: code Point.P)
    designation TEXT NOT NULL DEFAULT '',
    unit TEXT NOT NULL DEFAULT '',     -- U, ML, M2, KG, Boite...
    price_ht REAL NOT NULL,            -- prix convenu / negocie HT
    source TEXT NOT NULL DEFAULT 'import',   -- import | manuel
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (supplier_id, code)
);

CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    site_id INTEGER REFERENCES sites(id),
    doc_type TEXT NOT NULL DEFAULT 'facture',     -- facture | devis
    number TEXT NOT NULL DEFAULT '',
    date TEXT NOT NULL DEFAULT '',
    filename TEXT NOT NULL DEFAULT '',
    format TEXT NOT NULL DEFAULT '',              -- excel|csv|pdf|facturx|ubl|cii|ocr|manuel
    total_ht REAL NOT NULL DEFAULT 0,
    verified_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (supplier_id, doc_type, number, date)
);

CREATE TABLE IF NOT EXISTS invoice_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    line_no INTEGER NOT NULL DEFAULT 0,
    code TEXT NOT NULL DEFAULT '',
    designation TEXT NOT NULL DEFAULT '',
    unit TEXT NOT NULL DEFAULT '',
    quantity REAL NOT NULL DEFAULT 0,
    unit_price_ht REAL NOT NULL DEFAULT 0,
    line_total_ht REAL NOT NULL DEFAULT 0,
    ref_price_ht REAL,                 -- prix de reference trouve (NULL si absent)
    status TEXT NOT NULL DEFAULT 'pending',  -- ok | ecart | prix_absent
    diff_ht REAL NOT NULL DEFAULT 0    -- (prix facture - prix convenu) x quantite
);

CREATE TABLE IF NOT EXISTS missing_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    code TEXT NOT NULL DEFAULT '',
    designation TEXT NOT NULL DEFAULT '',
    unit TEXT NOT NULL DEFAULT '',
    last_price_seen REAL,
    occurrences INTEGER NOT NULL DEFAULT 1,
    resolved INTEGER NOT NULL DEFAULT 0,   -- 1 des que le prix est ajoute a la liste
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (supplier_id, code, designation)
);

CREATE INDEX IF NOT EXISTS idx_lines_invoice ON invoice_lines(invoice_id);
CREATE INDEX IF NOT EXISTS idx_lines_code ON invoice_lines(code);
CREATE INDEX IF NOT EXISTS idx_price_code ON price_items(supplier_id, code);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as db:
        db.executescript(SCHEMA)

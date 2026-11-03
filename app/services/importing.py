"""Imports : liste de prix, factures/devis (tous formats), chantiers, fournisseurs."""
from __future__ import annotations

import os
from typing import Optional

from ..db import get_db
from ..parsers.einvoice import looks_like_einvoice, parse_facturx, parse_ubl, parse_cii
from ..parsers.excel_csv import (InvoiceData, PriceRow, parse_invoice_file,
                                 parse_prices_file)
from ..parsers.pdf_simple import extract_text
from ..services.verification import upsert_price_item, verify_invoice


# ---------------------------------------------------------------------------
# Fournisseurs & chantiers
# ---------------------------------------------------------------------------
def get_or_create_supplier(name: str, tolerance: float = 0.01) -> int:
    name = name.strip()
    with get_db() as db:
        row = db.execute("SELECT id FROM suppliers WHERE name=?", (name,)).fetchone()
        if row:
            return row["id"]
        cur = db.execute("INSERT INTO suppliers (name, tolerance) VALUES (?,?)",
                         (name, tolerance))
        return cur.lastrowid


def get_or_create_site(name: str) -> Optional[int]:
    name = (name or "").strip()
    if not name:
        return None
    with get_db() as db:
        row = db.execute("SELECT id FROM sites WHERE name=?", (name,)).fetchone()
        if row:
            return row["id"]
        cur = db.execute("INSERT INTO sites (name) VALUES (?)", (name,))
        return cur.lastrowid


# ---------------------------------------------------------------------------
# Liste de prix
# ---------------------------------------------------------------------------
def import_price_list(supplier_id: int, filename: str, data: bytes) -> dict:
    rows: list[PriceRow] = parse_prices_file(filename, data)
    added = updated = 0
    with get_db() as db:
        existing = {r["code"].upper(): r["id"] for r in db.execute(
            "SELECT code, id FROM price_items WHERE supplier_id=?", (supplier_id,))}
    for r in rows:
        # ecrit directement dans la liste (upsert) sans re-verifier les factures
        # a chaque ligne -> gain de temps sur les grosses listes ; on re-verifie
        # ensuite en une seule passe toutes les factures du fournisseur.
        with get_db() as db:
            db.execute(
                """INSERT INTO price_items (supplier_id, code, designation, unit, price_ht, source)
                   VALUES (?,?,?,?,?,?)
                   ON CONFLICT(supplier_id, code) DO UPDATE SET
                     designation=excluded.designation, unit=excluded.unit,
                     price_ht=excluded.price_ht, source=excluded.source,
                     updated_at=datetime('now')""",
                (supplier_id, r.code.strip(), r.designation, r.unit, r.price_ht, "import"))
            db.execute("UPDATE missing_items SET resolved=1 WHERE supplier_id=? AND code=? AND resolved=0",
                       (supplier_id, r.code.strip()))
        if r.code.upper() in existing:
            updated += 1
        else:
            added += 1
    # re-verification globale des factures du fournisseur (une seule passe)
    touched = []
    with get_db() as db:
        touched = [row["id"] for row in db.execute(
            "SELECT id FROM invoices WHERE supplier_id=?", (supplier_id,))]
    for iid in touched:
        verify_invoice(iid)
    return {"imported": len(rows), "added": added, "updated": updated}


# ---------------------------------------------------------------------------
# Facture / devis
# ---------------------------------------------------------------------------
def _dispatch_parse(filename: str, data: bytes):
    """Retourne (InvoiceData|None, format_str, message_info)."""
    kind = looks_like_einvoice(filename, data)
    if kind == "facturx":
        try:
            return parse_facturx(data), "facturx", ""
        except ValueError:
            pass  # peut etre un PDF simple
    elif kind == "ubl":
        return parse_ubl(data), "ubl", ""
    elif kind == "cii":
        return parse_cii(data), "cii", ""

    low = filename.lower()
    if low.endswith((".xlsx", ".xlsm", ".xls", ".csv")):
        return parse_invoice_file(filename, data), ("excel" if "x" in low[-5:] else "csv"), ""
    if low.endswith(".pdf"):
        text = extract_text(data)
        return None, "pdf", ("PDF sans donnees structurées. Texte extrait ci-dessous ; "
                             "ajoutez les lignes manuellement ou recuperez la version "
                             "Factur-X/Excel.\n\n" + (text[:3000] if text else "(aucun texte lisible)"))
    if low.endswith((".png", ".jpg", ".jpeg", ".webp", ".heic")):
        return None, "ocr", ("Scan/photo : l'OCR sera actif en v0.2 (option tesseract). "
                             "Pour l'instant, saisissez les lignes manuellement.")
    return None, "?", f"Format non reconnu : {filename}"


def import_invoice(supplier_id: int, filename: str, data: bytes,
                   site_name: str = "", doc_type: str = "facture",
                   number: str = "", date: str = "") -> dict:
    parsed, fmt, info = _dispatch_parse(filename, data)
    site_id = get_or_create_site(site_name) if site_name else None
    result = {"format": fmt, "info": info, "invoice_id": None,
              "lines": 0, "stats": None}
    inv = parsed or InvoiceData()
    number = number or inv.number
    date = date or inv.date
    if not site_id and inv.site:
        site_id = get_or_create_site(inv.site)

    with get_db() as db:
        cur = db.execute(
            """INSERT INTO invoices (supplier_id, site_id, doc_type, number, date, filename, format)
               VALUES (?,?,?,?,?,?,?)
               ON CONFLICT(supplier_id, doc_type, number, date) DO UPDATE SET
                 filename=excluded.filename, format=excluded.format""",
            (supplier_id, site_id, doc_type, number or os.path.splitext(filename)[0][:64],
             date or "", filename, fmt))
        invoice_id = cur.lastrowid
        if invoice_id is None:
            invoice_id = db.execute(
                "SELECT id FROM invoices WHERE supplier_id=? AND doc_type=? AND number=? AND date=?",
                (supplier_id, doc_type, number or os.path.splitext(filename)[0][:64],
                 date or "")).fetchone()["id"]
        # remplace les lignes (re-import du meme fichier)
        db.execute("DELETE FROM invoice_lines WHERE invoice_id=?", (invoice_id,))
        for ln in inv.lines:
            db.execute(
                """INSERT INTO invoice_lines
                   (invoice_id, line_no, code, designation, unit, quantity,
                    unit_price_ht, line_total_ht) VALUES (?,?,?,?,?,?,?,?)""",
                (invoice_id, ln.line_no, ln.code, ln.designation, ln.unit,
                 ln.quantity, ln.unit_price_ht, ln.line_total_ht))
        result["invoice_id"] = invoice_id
        result["lines"] = len(inv.lines)

    if inv.lines:
        result["stats"] = verify_invoice(invoice_id)
    return result


def add_manual_line(invoice_id: int, code: str, designation: str, unit: str,
                    quantity: float, unit_price_ht: float) -> dict:
    with get_db() as db:
        nxt = db.execute("SELECT COALESCE(MAX(line_no),0)+1 n FROM invoice_lines WHERE invoice_id=?",
                         (invoice_id,)).fetchone()["n"]
        db.execute(
            """INSERT INTO invoice_lines
               (invoice_id, line_no, code, designation, unit, quantity, unit_price_ht, line_total_ht)
               VALUES (?,?,?,?,?,?,?,?)""",
            (invoice_id, nxt, code.strip(), designation.strip(), unit.strip(),
             quantity, unit_price_ht, round(quantity * unit_price_ht, 2)))
    return verify_invoice(invoice_id)

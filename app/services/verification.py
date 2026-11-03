"""Service de verification : compare chaque ligne facturee a la liste de prix.

Regles issues des audios du client :
  1. Rapprochement d'abord par CODE ARTICLE (code Point.P, ref fournisseur...),
     puis par DESIGNATION normalisee (fallback).
  2. Article absent de la liste de prix -> statut "prix_absent"
     ("je n'ai pas le prix de ca") + enregistrement dans missing_items.
     Des que le prix est complete dans la liste, l'article est resolu et
     les factures existantes sont re-verifiees.
  3. Ecart de prix -> montant de l'erreur = (prix facture - prix convenu) x quantite,
     calcule par ligne, par facture et au total global.
  4. Tolerance d'arrondi parametrisable par fournisseur (defaut 0.01 EUR).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

from ..db import get_db

# ---------------------------------------------------------------------------
# Normalisation / matching par designation
# ---------------------------------------------------------------------------
_STOPWORDS = {"le", "la", "les", "de", "du", "des", "un", "une", "et", "en"}


def normalize_designation(text: str) -> str:
    """Normalise une designation pour le rapprochement fallback.

    minuscules, sans accents, ponctuation -> espaces, unification des unites
    courantes (M2->m2, ML, LG...), suppression des mots vides.
    """
    t = unicodedata.normalize("NFKD", text or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^\w]+", " ", t)
    # unifications simples frequentes dans les materiaux
    t = (t.replace(" metre carre ", " m2 ").replace(" metre lineaire ", " ml ")
           .replace(" metrique ", " m ").replace(" piece ", " u "))
    words = [w for w in t.split() if w and w not in _STOPWORDS]
    return " ".join(words)


def similarity(a: str, b: str) -> float:
    """Similarite par recouvrement de tokens (suffisant et rapide sur RPi3)."""
    if not a or not b:
        return 0.0
    ta, tb = set(a.split()), set(b.split())
    inter = ta & tb
    if not inter:
        return 0.0
    return len(inter) / max(len(ta), len(tb))


DESIGNATION_MATCH_MIN = 0.60   # seuil de confiance du fallback par designation


# ---------------------------------------------------------------------------
# Recherche du prix de reference
# ---------------------------------------------------------------------------
def find_ref_price(db, supplier_id: int, code: str, designation: str):
    """Retourne (price_ht, source_match, price_item_id) ou (None, None, None).

    1) match exact par code article (normalise)
    2) fallback par designation normalisee identique
    3) fallback par similarite >= seuil (meilleur score)
    """
    norm_code = (code or "").strip().upper().replace(" ", "")
    if norm_code:
        row = db.execute(
            "SELECT id, price_ht FROM price_items WHERE supplier_id=? AND UPPER(REPLACE(TRIM(code),' ',''))=?",
            (supplier_id, norm_code),
        ).fetchone()
        if row:
            return row["price_ht"], "code", row["id"]

    nd = normalize_designation(designation)
    if nd:
        # match exact sur designation normalisee
        rows = db.execute(
            "SELECT id, price_ht, designation FROM price_items WHERE supplier_id=?",
            (supplier_id,),
        ).fetchall()
        best_score, best_row = 0.0, None
        for r in rows:
            rp = normalize_designation(r["designation"])
            if rp == nd:
                return r["price_ht"], "designation", r["id"]
            s = similarity(nd, rp)
            if s > best_score:
                best_score, best_row = s, r
        if best_row is not None and best_score >= DESIGNATION_MATCH_MIN:
            return best_row["price_ht"], "designation_proche", best_row["id"]
    return None, None, None


# ---------------------------------------------------------------------------
# Verification d'une facture complete
# ---------------------------------------------------------------------------
def verify_invoice(invoice_id: int) -> dict:
    """Verifie toutes les lignes d'une facture/devis vs liste de prix du fournisseur.

    Retourne un resume : nb lignes, ok, ecarts, prix_absents, total ecart EUR.
    """
    stats = {"invoice_id": invoice_id, "lines": 0, "ok": 0, "ecarts": 0,
             "prix_absents": 0, "total_ecart_ht": 0.0}
    with get_db() as db:
        inv = db.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()
        if inv is None:
            raise ValueError(f"Facture {invoice_id} introuvable")
        supplier_id = inv["supplier_id"]
        tol = db.execute("SELECT tolerance FROM suppliers WHERE id=?",
                         (supplier_id,)).fetchone()["tolerance"]

        lines = db.execute(
            "SELECT * FROM invoice_lines WHERE invoice_id=? ORDER BY line_no",
            (invoice_id,),
        ).fetchall()

        for ln in lines:
            stats["lines"] += 1
            qty = ln["quantity"] or 0.0
            billed = ln["unit_price_ht"] or 0.0
            ref_price, match_by, _pid = find_ref_price(
                db, supplier_id, ln["code"], ln["designation"])

            if ref_price is None:
                status, diff, stored_ref = "prix_absent", 0.0, None
                _register_missing(db, supplier_id, ln)
                stats["prix_absents"] += 1
            else:
                stored_ref = ref_price
                diff = round((billed - ref_price) * qty, 2)
                if abs(billed - ref_price) <= tol:
                    status, diff = "ok", 0.0
                    stats["ok"] += 1
                else:
                    status = "ecart"
                    stats["ecarts"] += 1
                    stats["total_ecart_ht"] += diff

            db.execute(
                "UPDATE invoice_lines SET ref_price_ht=?, status=?, diff_ht=? WHERE id=?",
                (stored_ref, status, diff, ln["id"]),
            )

        db.execute("UPDATE invoices SET verified_at=datetime('now') WHERE id=?",
                   (invoice_id,))
        stats["total_ecart_ht"] = round(stats["total_ecart_ht"], 2)

        # total facture recalcule
        tot = db.execute(
            "SELECT COALESCE(SUM(line_total_ht),0) t FROM invoice_lines WHERE invoice_id=?",
            (invoice_id,)).fetchone()["t"]
        db.execute("UPDATE invoices SET total_ht=? WHERE id=?", (round(tot, 2), invoice_id))
    return stats


def _register_missing(db, supplier_id: int, ln) -> None:
    """Met l'article a part avec 'je n'ai pas le prix de ca' (audio 1)."""
    existing = db.execute(
        "SELECT id, occurrences FROM missing_items WHERE supplier_id=? AND code=? AND designation=?",
        (supplier_id, ln["code"].strip(), ln["designation"].strip())).fetchone()
    if existing:
        db.execute("UPDATE missing_items SET occurrences=occurrences+1, last_price_seen=? WHERE id=?",
                   (ln["unit_price_ht"], existing["id"]))
    else:
        db.execute(
            "INSERT INTO missing_items (supplier_id, code, designation, unit, last_price_seen)"
            " VALUES (?,?,?,?,?)",
            (supplier_id, ln["code"].strip(), ln["designation"].strip(), ln["unit"], ln["unit_price_ht"]))


# ---------------------------------------------------------------------------
# Completion de la liste de prix -> re-verification automatique
# ---------------------------------------------------------------------------
def upsert_price_item(supplier_id: int, code: str, designation: str,
                      unit: str, price_ht: float, source: str = "manuel") -> int:
    """Ajoute/modifie un prix dans la liste de reference, resout les articles
    manquants correspondants et re-verifie les factures impactees."""
    code = (code or "").strip()
    with get_db() as db:
        cur = db.execute(
            """INSERT INTO price_items (supplier_id, code, designation, unit, price_ht, source)
               VALUES (?,?,?,?,?,?)
               ON CONFLICT(supplier_id, code) DO UPDATE SET
                 designation=excluded.designation, unit=excluded.unit,
                 price_ht=excluded.price_ht, source=excluded.source,
                 updated_at=datetime('now')""",
            (supplier_id, code, (designation or "").strip(), (unit or "").strip(), price_ht, source))
        pid = cur.lastrowid
        if pid is None:
            pid = db.execute("SELECT id FROM price_items WHERE supplier_id=? AND code=?",
                             (supplier_id, code)).fetchone()["id"]
        # resoudre l'article manquant correspondant
        db.execute(
            """UPDATE missing_items SET resolved=1
               WHERE supplier_id=? AND code=? AND resolved=0""",
            (supplier_id, code))
        # re-verifier les factures contenant ce code
        inv_ids = [r["invoice_id"] for r in db.execute(
            "SELECT DISTINCT invoice_id FROM invoice_lines WHERE code=? "
            "AND invoice_id IN (SELECT id FROM invoices WHERE supplier_id=?)",
            (code, supplier_id)).fetchall()]
    for iid in inv_ids:
        verify_invoice(iid)
    return pid


def global_stats() -> dict:
    """Chiffres pour le tableau de bord + audio 2 : recap par chantier."""
    out = {"suppliers": 0, "invoices": 0, "lines": 0, "ecarts": 0,
           "prix_absents": 0, "total_ecart_ht": 0.0, "sites": []}
    with get_db() as db:
        out["suppliers"] = db.execute("SELECT COUNT(*) c FROM suppliers").fetchone()["c"]
        out["invoices"] = db.execute("SELECT COUNT(*) c FROM invoices").fetchone()["c"]
        row = db.execute(
            """SELECT COUNT(*) lines,
                      SUM(status='ecart') ecarts,
                      SUM(status='prix_absent') absents,
                      COALESCE(SUM(diff_ht),0) tot
               FROM invoice_lines""").fetchone()
        out["lines"] = row["lines"] or 0
        out["ecarts"] = row["ecarts"] or 0
        out["prix_absents"] = row["absents"] or 0
        out["total_ecart_ht"] = round(row["tot"] or 0.0, 2)
        # recap achats matériaux par chantier (audio 2)
        out["sites"] = [dict(r) for r in db.execute(
            """SELECT s.name site, COUNT(DISTINCT i.id) nb_factures,
                      ROUND(COALESCE(SUM(l.line_total_ht),0),2) total_achats_ht,
                      ROUND(COALESCE(SUM(l.diff_ht),0),2) total_ecart_ht
               FROM sites s
               LEFT JOIN invoices i ON i.site_id=s.id
               LEFT JOIN invoice_lines l ON l.invoice_id=i.id
               GROUP BY s.id ORDER BY total_achats_ht DESC""").fetchall()]
    return out

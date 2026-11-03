"""Exports des ecarts : Excel (xlsx) et CSV, prets a envoyer au fournisseur
pour demander un avoir. Le PDF est ajoute si une lib dispo, sinon message clair."""
from __future__ import annotations

import csv
import io
import os
from datetime import datetime

from ..config import EXPORT_DIR
from ..db import get_db


def _fetch_discrepancies(supplier_id: int | None = None,
                         site_id: int | None = None,
                         include_missing: bool = True) -> list[dict]:
    q = """
      SELECT s.name fournisseur, st.name chantier, i.number facture, i.date,
             l.line_no, l.code, l.designation, l.unit, l.quantity,
             l.unit_price_ht pu_facture, l.ref_price_ht prix_convenu, l.diff_ht ecart,
             l.status
      FROM invoice_lines l
      JOIN invoices i ON i.id = l.invoice_id
      JOIN suppliers s ON s.id = i.supplier_id
      LEFT JOIN sites st ON st.id = i.site_id
      WHERE (l.status='ecart' OR (l.status='prix_absent' AND ?=1))
        AND (? IS NULL OR i.supplier_id=?)
        AND (? IS NULL OR i.site_id=?)
      ORDER BY s.name, i.date, l.line_no
    """
    with get_db() as db:
        rows = db.execute(q, (1 if include_missing else 0,
                              supplier_id, supplier_id, site_id, site_id)).fetchall()
    return [dict(r) for r in rows]


def export_discrepancies_xlsx(supplier_id=None, site_id=None) -> str:
    rows = _fetch_discrepancies(supplier_id, site_id)
    path = os.path.join(EXPORT_DIR, f"ecarts_{datetime.now():%Y%m%d_%H%M%S}.xlsx")
    try:
        import xlsxwriter
        wb = xlsxwriter.Workbook(path)
        ws = wb.add_worksheet("Ecarts")
        headers = ["Fournisseur", "Chantier", "Facture", "Date", "Ligne", "Code article",
                   "Designation", "Unite", "Quantite", "PU facture HT",
                   "Prix convenu HT", "Ecart HT", "Statut"]
        bold = wb.add_format({"bold": True})
        money = wb.add_format({"num_format": "#,##0.00"})
        red = wb.add_format({"font_color": "#b30000", "num_format": "#,##0.00"})
        for c, h in enumerate(headers):
            ws.write(0, c, h, bold)
        total = 0.0
        for r_i, r in enumerate(rows, start=1):
            ws.write(r_i, 0, r["fournisseur"] or "")
            ws.write(r_i, 1, r["chantier"] or "")
            ws.write(r_i, 2, r["facture"] or "")
            ws.write(r_i, 3, r["date"] or "")
            ws.write_number(r_i, 4, r["line_no"] or 0)
            ws.write(r_i, 5, r["code"] or "")
            ws.write(r_i, 6, r["designation"] or "")
            ws.write(r_i, 7, r["unit"] or "")
            ws.write_number(r_i, 8, r["quantity"] or 0, money)
            ws.write_number(r_i, 9, r["pu_facture"] or 0, money)
            ws.write_number(r_i, 10, r["prix_convenu"] if r["prix_convenu"] is not None else 0, money)
            ws.write_number(r_i, 11, r["ecart"] or 0, red)
            ws.write(r_i, 12, "PRIX ABSENT - a completer" if r["status"] == "prix_absent" else "ECART DE PRIX")
            total += (r["ecart"] or 0)
        trow = len(rows) + 1
        ws.write(trow, 10, "TOTAL PRETENDS RECLAMER HT :", bold)
        ws.write_number(trow, 11, round(total, 2), red)
        # Crédits / contact (demande d'avoir)
        from ..config import AUTHOR_NAME, AUTHOR_EMAIL
        ws.write(trow + 2, 0, f"Document prepare par {AUTHOR_NAME} (aidé par IA) - contact : {AUTHOR_EMAIL}")
        wb.close()
        return path
    except ImportError:
        # fallback CSV si xlsxwriter absent
        return export_discrepancies_csv(supplier_id, site_id)


def export_discrepancies_csv(supplier_id=None, site_id=None) -> str:
    rows = _fetch_discrepancies(supplier_id, site_id)
    path = os.path.join(EXPORT_DIR, f"ecarts_{datetime.now():%Y%m%d_%H%M%S}.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Fournisseur", "Chantier", "Facture", "Date", "Ligne", "Code article",
                    "Designation", "Unite", "Quantite", "PU facture HT",
                    "Prix convenu HT", "Ecart HT", "Statut"])
        for r in rows:
            w.writerow([r["fournisseur"], r["chantier"], r["facture"], r["date"],
                        r["line_no"], r["code"], r["designation"], r["unit"],
                        r["quantity"], r["pu_facture"], r["prix_convenu"],
                        r["ecart"], r["status"]])
    return path


def export_site_summary_xlsx() -> str:
    """Recapitulatif des achats par chantier (audio 2)."""
    path = os.path.join(EXPORT_DIR, f"recap_chantiers_{datetime.now():%Y%m%d_%H%M%S}.xlsx")
    with get_db() as db:
        rows = db.execute(
            """SELECT s.name chantier, COUNT(DISTINCT i.id) nb_factures,
                      ROUND(COALESCE(SUM(l.line_total_ht),0),2) total_achats_ht,
                      ROUND(COALESCE(SUM(l.diff_ht),0),2) total_ecart_ht
               FROM sites s
               LEFT JOIN invoices i ON i.site_id=s.id
               LEFT JOIN invoice_lines l ON l.invoice_id=i.id
               GROUP BY s.id ORDER BY total_achats_ht DESC""").fetchall()
    try:
        import xlsxwriter
        wb = xlsxwriter.Workbook(path)
        ws = wb.add_worksheet("Chantiers")
        bold = wb.add_format({"bold": True})
        money = wb.add_format({"num_format": "#,##0.00"})
        for c, h in enumerate(["Chantier", "Nb factures", "Total achats HT", "Total ecarts HT"]):
            ws.write(0, c, h, bold)
        for i, r in enumerate(rows, start=1):
            ws.write(i, 0, r["chantier"])
            ws.write_number(i, 1, r["nb_factures"])
            ws.write_number(i, 2, r["total_achats_ht"], money)
            ws.write_number(i, 3, r["total_ecart_ht"], money)
        wb.close()
        return path
    except ImportError:
        with open(path.replace(".xlsx", ".csv"), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Chantier", "Nb factures", "Total achats HT", "Total ecarts HT"])
            for r in rows:
                w.writerow([r["chantier"], r["nb_factures"], r["total_achats_ht"], r["total_ecart_ht"]])
        return path.replace(".xlsx", ".csv")

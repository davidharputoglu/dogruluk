"""Parsers Excel / CSV : listes de prix et factures.

Les en-tetes sont reconnus de facon souple (français, variantes Point.P).
Format attendu liste de prix : code | designation | unite | prix_ht
Format attendu facture      : code | designation | unite | quantite | pu_ht [total_ht]
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from typing import Iterable, Optional

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def to_float(v) -> Optional[float]:
    """Convertit '1 234,56 €', '12.345,00', 12.34 -> float ou None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("\u20ac", "").replace("€", "")
    s = re.sub(r"[^\d,.\-]", "", s)
    if not s or s in {"-", "."}:
        return None
    if "," in s and "." in s:
        # derniere ponctuation = separateur decimal
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


HEADER_ALIASES = {
    "code": ["code", "code article", "ref", "reference", "reference article",
             "article", "ean", "code barre", "item"],
    "designation": ["designation", "libelle", "description", "nom", "produit",
                    "article description", "intitule"],
    "unit": ["unite", "u", "um", "mesure"],
    "quantity": ["quantite", "qte", "qty", "nombre"],
    "pu_ht": ["pu ht", "pu", "prix unitaire", "prix unitaire ht", "prix ht",
              "prix unitaire hors taxe", "unit price"],
    "price": ["prix", "prix convenu", "prix negocie", "prix liste", "tarif",
              "prix net"],
    "total_ht": ["total ht", "montant ht", "total", "montant"],
}


def _norm_header(h: str) -> str:
    h = (h or "").lower()
    h = re.sub(r"[^\w ]+", " ", h)
    return re.sub(r"\s+", " ", h).strip()


def map_headers(headers: Iterable[str]) -> dict:
    """Retourne {champ_logique: index_colonne}."""
    mapping = {}
    normed = [_norm_header(h) for h in headers]
    for field_name, aliases in HEADER_ALIASES.items():
        for i, h in enumerate(normed):
            if any(a == h or a in h for a in aliases):
                if field_name not in mapping:
                    mapping[field_name] = i
                break
    return mapping


@dataclass
class PriceRow:
    code: str
    designation: str
    unit: str = ""
    price_ht: float = 0.0


@dataclass
class InvoiceData:
    number: str = ""
    date: str = ""
    site: str = ""
    lines: list = field(default_factory=list)   # list[InvoiceLine]


@dataclass
class InvoiceLine:
    line_no: int
    code: str
    designation: str
    unit: str
    quantity: float
    unit_price_ht: float
    line_total_ht: float


# ---------------------------------------------------------------------------
# Lecture tableur generique (listes de lignes de cellules)
# ---------------------------------------------------------------------------
def parse_price_table(rows: list[list], has_header: bool = True) -> list[PriceRow]:
    if not rows:
        return []
    start = 0
    if has_header:
        m = map_headers([str(c) if c is not None else "" for c in rows[0]])
        start = 1
    else:
        m = {"code": 0, "designation": 1, "unit": 2, "price": 3}
    out: list[PriceRow] = []
    for r in rows[start:]:
        if r is None or all(c in (None, "") for c in r):
            continue
        def cell(key, default=""):
            i = m.get(key)
            if i is None or i >= len(r) or r[i] is None:
                return default
            return r[i]
        code = str(cell("code")).strip()
        desig = str(cell("designation")).strip()
        price = to_float(cell("price")) or to_float(cell("pu_ht"))
        if not code and not desig:
            continue
        if price is None:
            continue  # ligne sans prix exploitable
        out.append(PriceRow(code=code, designation=desig,
                            unit=str(cell("unit")).strip(), price_ht=round(price, 4)))
    return out


def parse_invoice_table(rows: list[list], has_header: bool = True) -> InvoiceData:
    inv = InvoiceData()
    if not rows:
        return inv
    start = 0
    if has_header:
        m = map_headers([str(c) if c is not None else "" for c in rows[0]])
        start = 1
    else:
        m = {"code": 0, "designation": 1, "unit": 2, "quantity": 3, "pu_ht": 4}
    n = 0
    for r in rows[start:]:
        if r is None or all(c in (None, "") for c in r):
            continue
        def cell(key, default=""):
            i = m.get(key)
            if i is None or i >= len(r) or r[i] is None:
                return default
            return r[i]
        code = str(cell("code")).strip()
        desig = str(cell("designation")).strip()
        qty = to_float(cell("quantity"))
        pu = to_float(cell("pu_ht"))
        if not code and not desig:
            continue
        if qty is None and pu is None:
            continue
        qty = qty if qty is not None else 1.0
        pu = pu if pu is not None else 0.0
        total = to_float(cell("total_ht"))
        if total is None:
            total = round(qty * pu, 2)
        n += 1
        inv.lines.append(InvoiceLine(n, code, desig, str(cell("unit")).strip(),
                                     qty, round(pu, 4), round(total, 2)))
    return inv


# ---------------------------------------------------------------------------
# Fichiers
# ---------------------------------------------------------------------------
def read_csv_rows(data: bytes) -> list[list]:
    text = data.decode("utf-8-sig", errors="replace")
    sample = text[:4096]
    delim = ";" if sample.count(";") >= sample.count(",") else ","
    return [list(row) for row in csv.reader(io.StringIO(text), delimiter=delim)]


def read_xlsx_rows(data: bytes) -> list[list]:
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    ws = wb.active
    rows = [[c.value for c in row] for row in ws.iter_rows()]
    wb.close()
    return rows


def parse_prices_file(filename: str, data: bytes) -> list[PriceRow]:
    low = filename.lower()
    if low.endswith((".xlsx", ".xlsm")):
        rows = read_xlsx_rows(data)
    elif low.endswith((".xls",)):
        rows = read_xlsx_rows(data)  # .xls ancien format -> requiert conversion (v0.2)
    else:
        rows = read_csv_rows(data)
    return parse_price_table(rows)


def parse_invoice_file(filename: str, data: bytes) -> InvoiceData:
    low = filename.lower()
    if low.endswith((".xlsx", ".xlsm", ".xls")):
        rows = read_xlsx_rows(data)
    else:
        rows = read_csv_rows(data)
    return parse_invoice_table(rows)

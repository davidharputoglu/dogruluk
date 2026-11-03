"""Parsers facture electronique : Factur-X (PDF + XML ZUGFeRD), UBL, CII.

Depuis le 1er septembre 2026 les entreprises francaises doivent pouvoir recevoir
la facture electronique. Les donnees structurées (code article, quantite, prix HT,
ref chantier) sont lues directement -> pas d'OCR, pas d'erreur de lecture.

Implemente en v0.1 : extraction XML pure stdlib (pas de dependance lourde,
compatible ARM/ARM64). Le PDF d'un Factur-X est un PDF normal dont une piece
jointe embarque le XML ; on extrait aussi le XML colle dans le fichier .pdf.
"""
from __future__ import annotations

import io
import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from .excel_csv import InvoiceData, InvoiceLine


# ---------------------------------------------------------------------------
# Helpers namespaces
# ---------------------------------------------------------------------------
def _local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag.split(":")[-1]


def _findtext(el, name: str) -> str:
    for c in el.iter():
        if _local(c.tag) == name and c.text:
            return c.text.strip()
    return ""


def _findnum(el, name: str) -> float | None:
    t = _findtext(el, name)
    if not t:
        return None
    try:
        return float(t.replace(",", "."))
    except ValueError:
        return None


def _line_from(line_el, prefix: int) -> InvoiceLine | None:
    """Extrait une ligne d'un XML facture (noms de balises UN/CECF-like)."""
    code = ""
    # Identification du produit / line object
    for id_el in line_el.iter():
        ln = _local(id_el.tag)
        if ln in ("SellerAssignedID", "BuyerAssignedID", "GlobalID", "StandardTradeItemID"):
            if id_el.text and id_el.text.strip():
                code = id_el.text.strip()
                break
    designation = ""
    for n in ("Name", "Description", "LineContentDescription", "Note"):
        v = _findtext(line_el, n)
        if v:
            designation = v
            break
    qty = None
    for n in ("InvoicedQuantity", "CreditedQuantity", "Quantity", "BilledQuantity"):
        v = _findnum(line_el, n)
        if v is not None:
            qty = v
            break
    unit = ""
    for id_el in line_el.iter():
        if _local(id_el.tag) in ("InvoicedQuantity", "CreditedQuantity", "Quantity"):
            u = id_el.get("unitCode") or ""
            if u:
                unit = u
                break
    pu = None
    total = None
    for n in ("NetPrice", "GrossPrice", "PriceAmount", "ChargeAmount"):
        v = _findnum(line_el, n)
        if v is not None:
            pu = v
            break
    for n in ("LineTotalAmount", "SumLineExtendAmount", "ExtensionAmount"):
        v = _findnum(line_el, n)
        if v is not None:
            total = v
            break
    if not code and not designation:
        return None
    if qty is None and pu is None:
        return None
    qty = qty if qty is not None else 1.0
    pu = pu if pu is not None else 0.0
    total = total if total is not None else round(qty * pu, 2)
    return InvoiceLine(prefix, code, designation, unit, qty, pu, round(total, 2))


def _parse_generic_xml(xml_bytes: bytes) -> InvoiceData:
    """Detecte UBL / CII / ZUGFeRD et retourne un InvoiceData."""
    inv = InvoiceData()
    root = ET.fromstring(xml_bytes.decode("utf-8", errors="replace"))
    rname = _local(root.tag)

    # numero / date / chantier
    for n in ("ID", "DocumentNumber"):
        v = _findtext(root, n)
        if v:
            inv.number = v
            break
    for n in ("IssueDate", "DeliveryDate"):
        v = _findtext(root, n)
        if v:
            inv.date = v
            break
    for n in ("Reference", "BuyerReference", "ProjectReference", "ContractReference"):
        v = _findtext(root, n)
        if v:
            inv.site = v
            break

    line_tags = {
        "InvoiceLine",          # UBL
        "Line",                 # ZUGFeRD/CII (r:Line)
        "ReinvoicingLine",
    }
    i = 0
    for el in root.iter():
        if _local(el.tag) in line_tags:
            ln = _line_from(el, i + 1)
            if ln:
                i += 1
                ln.line_no = i
                inv.lines.append(ln)
    return inv


# ---------------------------------------------------------------------------
# Entrées par type de fichier
# ---------------------------------------------------------------------------
def parse_ubl(data: bytes) -> InvoiceData:
    return _parse_generic_xml(data)


def parse_cii(data: bytes) -> InvoiceData:
    return _parse_generic_xml(data)


def parse_facturx(data: bytes) -> InvoiceData:
    """Factur-X = PDF avec XML embarqué (attachment 'factur-x.xml')."""
    bio = io.BytesIO(data)
    if zipfile.is_zipfile(bio):
        with zipfile.ZipFile(bio) as z:
            for name in z.namelist():
                low = name.lower()
                if low.endswith(".xml") and any(k in low for k in
                        ("factur-x", "zugferd", "xml")):
                    return _parse_generic_xml(z.read(name))
    # fallback : cherche le bloc XML colle dans le fichier (certains exports)
    m = re.search(rb"<\?xml.*?</(?:rsm|CrossIndustry|Invoice)[^>]*>", data, re.S)
    if m:
        try:
            return _parse_generic_xml(m.group(0))
        except ET.ParseError:
            pass
    raise ValueError("Aucun XML Factur-X trouve dans le PDF")


def looks_like_einvoice(filename: str, data: bytes) -> str | None:
    """Retourne 'facturx'|'ubl'|'cii'|None selon le contenu."""
    low = filename.lower()
    head = data[:2048].decode("utf-8", errors="replace").lower()
    if low.endswith(".xml"):
        if "universalbusinesslanguage" in head or "ubl:" in head:
            return "ubl"
        if "crossindustryinvoice" in head or "faxml" in head or "rsm:" in head:
            return "cii"   # CII / ZUGFeRD
        return "cii"
    if low.endswith(".pdf") and b"factur-x" in data[:4096].lower():
        return "facturx"
    return None

"""PDF simple : extraction du texte avec pypdf (si disponible).

Un PDF sans donnees structurées n'est PAS fiable pour les lignes de facture :
en v0.1 on extrait le texte et on propose une saisie/verification manuelle ou
l'import du meme document en Factur-X / Excel. Le scan/photo (OCR) est prevu
en v0.2 (tesseract, optionnel sur RPi3).
"""
from __future__ import annotations


def extract_text(data: bytes) -> str:
    try:
        import io
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except Exception:
        return ""

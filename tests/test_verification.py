"""Tests de bout en bout du moteur de verification (sans serveur HTTP).

Couvre les regles des 2 audios :
  - ecart = (prix facture - prix convenu) x quantite, par ligne/facture/total
  - article absent -> "je n'ai pas le prix de ca" puis completion + re-verification
  - tolerance arrondis
  - recap par chantier
"""
from __future__ import annotations

import os
import sys
import tempfile

# base dediee aux tests
_tmp = tempfile.mkdtemp(prefix="vdf_test_")
os.environ["VDF_DATA_DIR"] = _tmp
os.environ["VDF_EXPORT_DIR"] = _tmp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db import init_db                      # noqa: E402
from app.services import importing              # noqa: E402
from app.services.verification import global_stats, verify_invoice  # noqa: E402


def setup_module(_=None):
    init_db()


def test_full_flow():
    sid = importing.get_or_create_supplier("Point.P Test", tolerance=0.01)
    site_id = importing.get_or_create_site("Chantier Maison Durand")

    csv_prices = ("Code article;Designation;Unite;Prix HT\n"
                  "100234567;Ciment CPA 45 - sac 35kg;U;6,20\n"
                  "100987654;Parpaing 20x20x50 creux;U;1,85\n").encode()
    res = importing.import_price_list(sid, "liste.csv", csv_prices)
    assert res["imported"] == 2

    csv_inv = ("Reference;Designation;Unite;Quantite;PU HT\n"
               "100234567;CIMENT CPA 45 SAC 35KG;U;150;6,20\n"     # conforme (code)
               "100987654;Parpaing 20x20x50 creux;U;400;2,10\n"    # ecart (2,10-1,85)*400=100
               "777000888;Treillis soude ST25 6m;U;20;34,90\n").encode()  # prix absent
    r = importing.import_invoice(sid, "facture.csv", csv_inv,
                                 site_name="Chantier Maison Durand", number="FA-001", date="2026-11-01")
    stats = r["stats"]
    assert stats["lines"] == 3
    assert stats["ok"] == 1
    assert stats["ecarts"] == 1
    assert stats["prix_absents"] == 1
    assert abs(stats["total_ecart_ht"] - 100.0) < 1e-6   # montant de l'erreur

    # article manquant bien mis a part
    g = global_stats()
    assert any(s["site"] == "Chantier Maison Durand" for s in g["sites"])
    rec = [s for s in g["sites"] if s["site"] == "Chantier Maison Durand"][0]
    assert abs(rec["total_ecart_ht"] - 100.0) < 1e-6

    # on complete le prix manquant -> re-verification automatique
    importing.upsert_price_item(sid, "777000888", "Treillis soude ST25 6m", "U", 34.90)
    st2 = verify_invoice(r["invoice_id"])
    assert st2["prix_absents"] == 0 and st2["ok"] == 2 and st2["ecarts"] == 1

    # tolérance : 6,20 vs 6,205 facturé avec tol 0.01 -> conforme
    csv_tol = ("Reference;Designation;Unite;Quantite;PU HT\n"
               "100234567;Ciment CPA 45 - sac 35kg;U;10;6,205\n").encode()
    rt = importing.import_invoice(sid, "tol.csv", csv_tol, number="FA-TOL")
    assert rt["stats"]["ok"] == 1 and rt["stats"]["ecarts"] == 0


def test_einvoice_ubl():
    ubl = b"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">
  <cbc:ID xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">UBL-42</cbc:ID>
  <cbc:IssueDate xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">2026-11-02</cbc:IssueDate>
  <cbc:BuyerReference xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">Chantier UBL</cbc:BuyerReference>
  <cac:InvoiceLine xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
    <cbc:ID xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">1</cbc:ID>
    <cbc:InvoicedQuantity xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" unitCode="H87">10.0</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">62.00</cbc:LineExtensionAmount>
    <cac:Price xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
      <cbc:PriceAmount xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">6.20</cbc:PriceAmount>
    </cac:Price>
    <cac:Item xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
      <cbc:Description xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">Ciment CPA 45 - sac 35kg</cbc:Description>
      <cac:SellersItemIdentification xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
        <cbc:ID xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">100234567</cbc:ID>
      </cac:SellersItemIdentification>
    </cac:Item>
  </cac:InvoiceLine>
</Invoice>"""
    sid = importing.get_or_create_supplier("Point.P Test")
    r = importing.import_invoice(sid, "facture.xml", ubl, number="", date="")
    assert r["format"] == "ubl" and r["lines"] == 1
    assert r["stats"]["ok"] == 1   # prix retrouve par code 100234567


if __name__ == "__main__":
    setup_module()
    test_full_flow()
    test_einvoice_ubl()
    print("OK - tous les tests passent")

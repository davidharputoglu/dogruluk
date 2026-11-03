"""Application FastAPI principale : UI (Jinja2) + API JSON."""
from __future__ import annotations

import os

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import APP_NAME, APP_TAGLINE, EDITION, VERSION, HOST, PORT, FEATURE_EMAIL_IMPORT, FEATURE_WATCHED_FOLDER
from .db import init_db, get_db
from .services import importing, exporting
from .services.verification import verify_invoice, upsert_price_item, global_stats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
templates.env.globals.update(APP_NAME=APP_NAME, APP_TAGLINE=APP_TAGLINE,
                             VERSION=VERSION, EDITION=EDITION,
                             FEATURE_EMAIL_IMPORT=FEATURE_EMAIL_IMPORT,
                             FEATURE_WATCHED_FOLDER=FEATURE_WATCHED_FOLDER)


@app.on_event("startup")
def _startup():
    init_db()


# ---------------------------------------------------------------------------
# Tableau de bord
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html",
                                       {"request": request, "stats": global_stats()})


# ---------------------------------------------------------------------------
# Fournisseurs
# ---------------------------------------------------------------------------
@app.post("/suppliers")
def add_supplier(name: str = Form(...), tolerance: float = Form(0.01)):
    sid = importing.get_or_create_supplier(name, tolerance)
    return RedirectResponse(f"/suppliers/{sid}", status_code=303)


@app.get("/suppliers/{sid}", response_class=HTMLResponse)
def supplier_page(request: Request, sid: int):
    with get_db() as db:
        sup = db.execute("SELECT * FROM suppliers WHERE id=?", (sid,)).fetchone()
        prices = db.execute("SELECT * FROM price_items WHERE supplier_id=? ORDER BY code LIMIT 500",
                            (sid,)).fetchall()
        missing = db.execute("SELECT * FROM missing_items WHERE supplier_id=? AND resolved=0 "
                             "ORDER BY occurrences DESC", (sid,)).fetchall()
        invoices = db.execute("""SELECT i.*, s2.name site FROM invoices i
                                 LEFT JOIN sites s2 ON s2.id=i.site_id
                                 WHERE i.supplier_id=? ORDER BY i.created_at DESC""", (sid,)).fetchall()
        if sup is None:
            return HTMLResponse("Fournisseur inconnu", status_code=404)
        return templates.TemplateResponse("supplier.html", {
            "request": request, "sup": sup, "prices": prices,
            "missing": missing, "invoices": invoices, "n_prices": len(prices)})


@app.post("/suppliers/{sid}/prices")
def add_price(sid: int, code: str = Form(...), designation: str = Form(""),
              unit: str = Form(""), price_ht: float = Form(...)):
    upsert_price_item(sid, code, designation, unit, price_ht)
    return RedirectResponse(f"/suppliers/{sid}", status_code=303)


@app.post("/suppliers/{sid}/price-list")
async def import_price_list(sid: int, file: UploadFile = File(...)):
    data = await file.read()
    res = importing.import_price_list(sid, file.filename or "liste.csv", data)
    return JSONResponse(res)


# ---------------------------------------------------------------------------
# Factures / devis
# ---------------------------------------------------------------------------
@app.post("/suppliers/{sid}/invoices")
async def import_invoice(sid: int, file: UploadFile = File(...),
                         site: str = Form(""), doc_type: str = Form("facture"),
                         number: str = Form(""), date: str = Form("")):
    data = await file.read()
    res = importing.import_invoice(sid, file.filename or "doc", data,
                                   site_name=site, doc_type=doc_type,
                                   number=number, date=date)
    if res["invoice_id"] and res["lines"]:
        return RedirectResponse(f"/invoices/{res['invoice_id']}", status_code=303)
    # PDF simple / scan : facture creee sans lignes -> page de saisie manuelle
    return RedirectResponse(f"/invoices/{res['invoice_id']}", status_code=303)


@app.get("/invoices/{iid}", response_class=HTMLResponse)
def invoice_page(request: Request, iid: int):
    with get_db() as db:
        inv = db.execute("""SELECT i.*, s.name fournisseur, st.name site
                            FROM invoices i JOIN suppliers s ON s.id=i.supplier_id
                            LEFT JOIN sites st ON st.id=i.site_id WHERE i.id=?""",
                         (iid,)).fetchone()
        lines = db.execute("SELECT * FROM invoice_lines WHERE invoice_id=? ORDER BY line_no",
                           (iid,)).fetchall()
    if inv is None:
        return HTMLResponse("Facture introuvable", status_code=404)
    stats = verify_invoice(iid)   # re-verifie a l'ouverture (prix completes depuis)
    return templates.TemplateResponse("invoice.html",
                                      {"request": request, "inv": inv, "lines": lines, "stats": stats})


@app.post("/invoices/{iid}/lines")
def add_line(iid: int, code: str = Form(""), designation: str = Form(...),
             unit: str = Form(""), quantity: float = Form(1), pu_ht: float = Form(...)):
    importing.add_manual_line(iid, code, designation, unit, quantity, pu_ht)
    return RedirectResponse(f"/invoices/{iid}", status_code=303)


@app.post("/invoices/{iid}/reverify")
def reverify(iid: int):
    return JSONResponse(verify_invoice(iid))


# ---------------------------------------------------------------------------
# Chantiers (audio 2)
# ---------------------------------------------------------------------------
@app.get("/sites", response_class=HTMLResponse)
def sites_page(request: Request):
    stats = global_stats()
    return templates.TemplateResponse("sites.html", {"request": request, "sites": stats["sites"]})


@app.post("/sites")
def add_site(name: str = Form(...)):
    importing.get_or_create_site(name)
    return RedirectResponse("/sites", status_code=303)


@app.get("/sites/{site_id}", response_class=HTMLResponse)
def site_detail(request: Request, site_id: int):
    with get_db() as db:
        site = db.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
        invoices = db.execute("""SELECT i.*, s.name fournisseur FROM invoices i
                                 JOIN suppliers s ON s.id=i.supplier_id
                                 WHERE i.site_id=? ORDER BY i.date DESC""", (site_id,)).fetchall()
        totals = db.execute("""SELECT ROUND(COALESCE(SUM(l.line_total_ht),0),2) t,
                                      ROUND(COALESCE(SUM(l.diff_ht),0),2) e
                               FROM invoice_lines l WHERE l.invoice_id IN
                               (SELECT id FROM invoices WHERE site_id=?)""", (site_id,)).fetchone()
    return templates.TemplateResponse("site_detail.html", {
        "request": request, "site": site, "invoices": invoices, "totals": dict(totals)})


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
@app.get("/export/ecarts")
def export_ecarts(supplier_id: int | None = None, site_id: int | None = None, fmt: str = "xlsx"):
    path = (exporting.export_discrepancies_csv(supplier_id, site_id) if fmt == "csv"
            else exporting.export_discrepancies_xlsx(supplier_id, site_id))
    return FileResponse(path, filename=os.path.basename(path))


@app.get("/export/chantiers")
def export_chantiers():
    path = exporting.export_site_summary_xlsx()
    return FileResponse(path, filename=os.path.basename(path))


# ---------------------------------------------------------------------------
# API JSON (pour futures integrations : mail, dossier surveille, mobile)
# ---------------------------------------------------------------------------
@app.get("/api/stats")
def api_stats():
    return global_stats()


def run():
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT)


if __name__ == "__main__":
    run()

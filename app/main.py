"""Application FastAPI principale : UI (Jinja2) + API JSON."""
from __future__ import annotations

import os

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import APP_NAME, APP_TAGLINE, EDITION, VERSION, HOST, PORT, FEATURE_EMAIL_IMPORT, FEATURE_WATCHED_FOLDER, AUTHOR_NAME, AUTHOR_EMAIL, AUTHOR_CREDIT
from .db import init_db, get_db
from .services import importing, exporting
from .services.verification import verify_invoice, upsert_price_item, global_stats
from . import i18n, settings as app_settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
templates.env.globals.update(APP_NAME=APP_NAME, APP_TAGLINE=APP_TAGLINE,
                             VERSION=VERSION, EDITION=EDITION,
                             AUTHOR_NAME=AUTHOR_NAME, AUTHOR_EMAIL=AUTHOR_EMAIL,
                             AUTHOR_CREDIT=AUTHOR_CREDIT,
                             FEATURE_EMAIL_IMPORT=FEATURE_EMAIL_IMPORT,
                             FEATURE_WATCHED_FOLDER=FEATURE_WATCHED_FOLDER)


def _lang_ctx(request: Request):
    """Langue effective : cookie `lang` > reglage UI > Accept-Language > defaut."""
    s = app_settings.all_settings()
    lang = i18n.pick_lang(request.cookies.get("lang"),
                          request.headers.get("accept-language"))
    if not request.cookies.get("lang") and s.get("language"):
        lang = i18n.normalize(s["language"])
    return {"LANG": lang, "RTL": lang in i18n.RTL_LANGS,
            "t": i18n.tr_ctx(lang), "LANGS": i18n.LANG_LABELS,
            "SETTINGS": s,
            "APP_DISPLAY_NAME": s.get("app_name") or APP_NAME,
            "EDITOR_NAME": s.get("editor_name") or AUTHOR_NAME,
            "EDITOR_EMAIL": s.get("editor_email") or AUTHOR_EMAIL}


def render(template: str, ctx: dict, request: Request | None = None):
    """Rendu Jinja avec la langue effective fusionnee dans le contexte.

    (Correction du bug de recursion : l'ancien corps rappelait ce meme
    `render` au lieu d'appeler templates.TemplateResponse.)
    """
    req = request if request is not None else ctx.get("request")
    merged = {**(_lang_ctx(req) if req is not None else {}), **ctx, "request": req}
    return templates.TemplateResponse(template, merged)


@app.get("/langue")
def set_lang(lang: str = "fr"):
    resp = RedirectResponse(url="/", status_code=302)
    resp.set_cookie("lang", i18n.normalize(lang), max_age=60 * 60 * 24 * 365,
                    samesite="lax")
    return resp


# ---------------------------------------------------------------------------
# Reglages (/parametres) — langue, nom, tolerance, devise, editeur
# ---------------------------------------------------------------------------
@app.get("/parametres", response_class=HTMLResponse)
def settings_page(request: Request):
    s = app_settings.all_settings()
    return render("settings.html", {
        "request": request,
        "s": _SettingsNS({
            "app_name": s["app_name"], "language": s["language"] or "",
            "tolerance": s["tolerance_default"], "currency": s["currency"],
            "editor_name": s["editor_name"], "editor_email": s["editor_email"]}),
        "langs": i18n.LANG_LABELS})


class _SettingsNS(dict):
    """Acces attribut dans le template (s.app_name) + valeurs sures."""
    def __getattr__(self, item):
        return self.get(item, "")


@app.post("/parametres")
def save_settings(request: Request,
                  app_name: str = Form(""), language: str = Form(""),
                  tolerance: str = Form("0.01"), currency: str = Form("EUR"),
                  editor_name: str = Form(""), editor_email: str = Form("")):
    try:
        tol = float(tolerance.replace(",", "."))
    except ValueError:
        tol = 0.01
    app_settings.set_many({
        "app_name": app_name.strip(),
        "language": i18n.normalize(language) if language else "",
        "tolerance_default": f"{max(0.0, tol):.2f}",
        "currency": currency.strip() or "EUR",
        "editor_name": editor_name.strip(),
        "editor_email": editor_email.strip(),
    })
    return RedirectResponse("/parametres", status_code=303)


# ---------------------------------------------------------------------------
# Pages legales (mentions / confidentialite / licence) — FR + EN,
# les autres langues retombent sur l'anglais (fallback i18n).
# ---------------------------------------------------------------------------
LICENSE_NAME = "Licence Doğruluk 1.0 (usage interne libre, redistribution commerciale interdite sans accord écrit)"
YEAR = "2026"


def _legal_ctx(request: Request) -> dict:
    s = app_settings.all_settings()
    return {"request": request,
            "editor_name": s.get("editor_name") or AUTHOR_NAME,
            "editor_email": s.get("editor_email") or AUTHOR_EMAIL,
            "LICENSE": LICENSE_NAME, "YEAR": YEAR}


@app.get("/mentions-legales", response_class=HTMLResponse)
def legal_mentions(request: Request):
    return render("legal.html", _legal_ctx(request))


@app.get("/confidentialite", response_class=HTMLResponse)
def privacy(request: Request):
    return render("privacy.html", _legal_ctx(request))


@app.get("/licence", response_class=HTMLResponse)
def license_page(request: Request):
    return render("license.html", _legal_ctx(request))


@app.on_event("startup")
def _startup():
    init_db()


# ---------------------------------------------------------------------------
# Tableau de bord
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return render("dashboard.html",
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
        return render("supplier.html", {
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
    return render("invoice.html",
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
    return render("sites.html", {"request": request, "sites": stats["sites"]})


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
    return render("site_detail.html", {
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


@app.get("/api/info")
def api_info():
    return {"app": APP_NAME, "version": VERSION, "edition": EDITION,
            "author": AUTHOR_NAME, "email": AUTHOR_EMAIL,
            "credit": AUTHOR_CREDIT}


def run():
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT)


if __name__ == "__main__":
    run()

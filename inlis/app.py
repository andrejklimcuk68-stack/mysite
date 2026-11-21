import os
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, Response
from werkzeug.middleware.proxy_fix import ProxyFix
from i18n import T

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # справжній https за проксі Render
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 86400
ADDRESS = "вулиця Павленка, Ірпінь, Київська область, 08200"
MAPS = "https://maps.app.goo.gl/1uqfXFVoQYsruSJF8"  # кнопка «Де ми» веде на це місце в Google Maps
PHONE = ("+380634592337", "+38 063 459 23 37")
LANGS = ("uk", "ru", "en")


def pre(lang):
    return "" if lang == "uk" else "/" + lang


def render(tpl, lang, page, **kw):
    root = request.url_root.rstrip("/")
    alts = {l: root + pre(l) + page for l in LANGS}
    return render_template(tpl, lang=lang, t=T[lang], alts=alts, L=lambda p: pre(lang) + p, maps=MAPS,
                           phone=PHONE, ga_id=os.environ.get("GA_ID", ""), **kw)


@app.context_processor
def static_helpers():
    def sv(filename: str, **kw) -> str:
        """url_for('static') з версією за mtime, щоб браузер не тримав застарілий CSS/JS/фото."""
        path = os.path.join(app.static_folder, filename)
        v = int(os.path.getmtime(path)) if os.path.exists(path) else 0
        return url_for("static", filename=filename, v=v, **kw)
    return {"sv": sv}


@app.after_request
def headers(r):
    r.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "SAMEORIGIN"
    r.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return r


@app.route("/", defaults={"lang": "uk"})
@app.route("/<any(ru,en):lang>/")
def home(lang):
    return render("index.html", lang, "/")


@app.route("/privacy", defaults={"lang": "uk"})
@app.route("/<any(ru,en):lang>/privacy")
def privacy(lang):
    return render("legal.html", lang, "/privacy", doc=T[lang]["privacy"])


@app.route("/terms", defaults={"lang": "uk"})
@app.route("/<any(ru,en):lang>/terms")
def terms(lang):
    return render("legal.html", lang, "/terms", doc=T[lang]["terms"])


@app.route("/robots.txt")
def robots():
    return Response(f"User-agent: *\nAllow: /\n\nSitemap: {url_for('sitemap', _external=True)}\n", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    root = request.url_root.rstrip("/")
    urls = "".join(f"<url><loc>{root}{pre(l)}{p}</loc></url>" for l in LANGS for p in ("/", "/privacy", "/terms"))
    return Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    + urls + "</urlset>", mimetype="application/xml")


@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.svg"))


@app.errorhandler(404)
def nf(e):
    lang = next((l for l in ("ru", "en") if request.path.startswith("/" + l + "/")), "uk")
    return render("404.html", lang, "/"), 404


if __name__ == "__main__":
    app.run(debug=True)

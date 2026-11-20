import os, re, time, json, urllib.request
from collections import defaultdict, deque
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, Response
from itsdangerous import URLSafeTimedSerializer, BadSignature
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # справжні https та IP за проксі Render
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(24).hex()  # секрет лише на сервері
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 86400
ser = URLSafeTimedSerializer(app.config["SECRET_KEY"])
SITE = "Затишок"  # <-- назва вашого закладу
TO = os.environ.get("CONTACT_EMAIL") or "andrejklimcuk68@gmail.com"
PHONE = re.compile(r"^\+?[\d\s()-]{9,18}$")
hits = defaultdict(deque)


def send_mail(f):
    """Лист через HTTPS-API Resend (SMTP на безкоштовному Render заблоковано)."""
    print("НОВА ЗАЯВКА:", f, flush=True)  # запасна копія в Logs
    key = os.environ.get("RESEND_API_KEY")
    if not key:
        return False
    one = lambda t: t.replace("\n", " ").replace("\r", " ")
    text = (f"Ім’я: {one(f['name'])}\nТелефон: {f['phone']}\nГостей: {f['guests']}\n"
            f"Коли: {f['when']}\nПобажання: {one(f['note'])}")
    body = json.dumps({"from": "Сайт <onboarding@resend.dev>", "to": [TO],
                       "subject": "Нова бронь від " + one(f["name"]), "text": text}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", body, {
        "Authorization": "Bearer " + key, "Content-Type": "application/json", "User-Agent": "cafe/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status < 300
    except Exception as e:
        print("Помилка пошти:", e, flush=True)
        return False


@app.context_processor
def inject():
    return dict(site=SITE, to=TO, ga_id=os.environ.get("GA_ID", ""))


@app.after_request
def headers(r):
    r.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "SAMEORIGIN"
    r.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return r


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/book", methods=["GET", "POST"])
def book():
    f, err, sent = {}, {}, False
    if request.method == "POST":
        f = {k: request.form.get(k, "").strip() for k in ("name", "phone", "guests", "when", "note")}
        try:  # підписаний токен: захист від підробки + час відкриття форми
            age = time.time() - ser.loads(request.form.get("t", ""), max_age=7200)
        except BadSignature:
            age = -1
        q = hits[request.remote_addr]
        while q and time.time() - q[0] > 600:
            q.popleft()
        if request.form.get("website") or age < 3:  # пастка для ботів / надто швидко
            err["form"] = "Не вдалося надіслати. Оновіть сторінку й спробуйте ще раз."
        elif len(q) >= 3:
            err["form"] = "Забагато заявок. Спробуйте через 10 хвилин."
        else:
            if not 2 <= len(f["name"]) <= 60:
                err["name"] = "Ім’я: від 2 до 60 символів."
            if not PHONE.match(f["phone"]):
                err["phone"] = "Введіть телефон, наприклад +380 50 123 4567."
            if not f["guests"].isdigit() or not 1 <= int(f["guests"]) <= 12:
                err["guests"] = "Кількість гостей: від 1 до 12."
            try:
                datetime.strptime(f["when"], "%Y-%m-%dT%H:%M")
            except ValueError:
                err["when"] = "Оберіть дату й час."
            if len(f["note"]) > 300 or "http" in f["note"].lower():
                err["note"] = "Побажання: до 300 символів, без посилань."
            if not err:
                if send_mail(f):
                    q.append(time.time())
                    sent = True
                else:
                    err["form"] = "Не вдалося надіслати. Напишіть нам: " + TO
    return render_template("book.html", f=f, err=err, sent=sent, token=ser.dumps(time.time()))


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/robots.txt")
def robots():
    return Response(f"User-agent: *\nAllow: /\n\nSitemap: {url_for('sitemap', _external=True)}\n", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    urls = "".join(f"<url><loc>{url_for(p, _external=True)}</loc></url>" for p in ("home", "book", "privacy", "terms"))
    return Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    + urls + "</urlset>", mimetype="application/xml")


@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.svg"))


@app.errorhandler(404)
def nf(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

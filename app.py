import os, re, time
from collections import defaultdict, deque
from flask import Flask, render_template, redirect, request, url_for, Response
from itsdangerous import URLSafeTimedSerializer, BadSignature
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# Render стоит за прокси: так Flask видит настоящие https-адрес и IP посетителя
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
# Секреты берутся из переменных окружения на сервере, а не из кода и не из браузера
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(24).hex()
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 86400  # кеш статики на сутки
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

SITE_NAME = "Мой сайт"   # <-- поменяй на своё название
TOTAL_TABS = 20
hits = defaultdict(deque)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.context_processor
def inject():
    return dict(
        site_name=SITE_NAME,
        total=TOTAL_TABS,
        contact_email=os.environ.get("CONTACT_EMAIL", "your@email.com"),
        ga_id=os.environ.get("GA_ID", ""),
    )


@app.after_request
def security_headers(r):
    r.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "SAMEORIGIN"
    r.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return r


@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/tab/<int:number>")
def tab(number):
    if not 1 <= number <= TOTAL_TABS:
        return redirect(url_for("tab", number=1))
    prev_n = number - 1 if number > 1 else TOTAL_TABS
    next_n = number + 1 if number < TOTAL_TABS else 1
    return render_template("tab.html", current=number, prev_n=prev_n, next_n=next_n)


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form, errors, sent = {}, {}, False
    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in ("name", "email", "message")}
        try:  # токен = защита от подделки формы + время, когда её открыли
            age = time.time() - serializer.loads(request.form.get("t", ""), max_age=7200)
        except BadSignature:
            age = -1
        q = hits[request.remote_addr]
        while q and time.time() - q[0] > 600:
            q.popleft()
        if request.form.get("website") or age < 3:  # ловушка для ботов / слишком быстро
            errors["form"] = "Не удалось отправить. Обновите страницу и попробуйте снова."
        elif len(q) >= 3:
            errors["form"] = "Слишком много сообщений. Попробуйте через 10 минут."
        else:
            if not 2 <= len(form["name"]) <= 60:
                errors["name"] = "Имя: от 2 до 60 символов."
            if not EMAIL_RE.match(form["email"]) or len(form["email"]) > 120:
                errors["email"] = "Введите email в формате name@example.com."
            if not 10 <= len(form["message"]) <= 2000:
                errors["message"] = "Сообщение: от 10 до 2000 символов."
            elif form["message"].lower().count("http") > 2:
                errors["message"] = "В сообщении слишком много ссылок."
            if not errors:
                q.append(time.time())
                print("НОВОЕ СООБЩЕНИЕ:", form, flush=True)  # смотри во вкладке Logs на Render
                sent = True
    return render_template("contact.html", form=form, errors=errors, sent=sent,
                           token=serializer.dumps(time.time()))


@app.route("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\n\nSitemap: {url_for('sitemap', _external=True)}\n"
    return Response(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    pages = [url_for("home", _external=True)] + [url_for("tab", number=n, _external=True) for n in range(1, TOTAL_TABS + 1)]
    pages += [url_for(p, _external=True) for p in ("privacy", "terms", "contact")]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           + "".join(f"<url><loc>{u}</loc></url>" for u in pages) + "</urlset>")
    return Response(xml, mimetype="application/xml")


@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.svg"))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

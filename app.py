#!/usr/bin/env python3
"""
TIE Checker WebApp — Flask backend (dynamic)
"""

import urllib.request, urllib.parse, http.cookiejar, re, json, os
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

OFFICES_FILE = os.path.join(os.path.dirname(__file__), "static", "offices.json")

with open(OFFICES_FILE) as f:
    OFFICES_DATA = json.load(f)

def check_tie(province, office, office_id, lote, year="2026"):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    ]
    resp = opener.open("https://form24.es/lote/tie-status")
    html = resp.read().decode()
    m = re.search(r'name="_token" value="([^"]+)"', html)
    if not m:
        raise RuntimeError("Could not extract CSRF token")
    token = m.group(1)
    data = urllib.parse.urlencode({
        "_token": token,
        "provinces": province,
        "officine": office,
        "officine_id": office_id,
        "client_lote": lote,
        "year": year,
        "usr_agent": "tie_checker",
    }).encode()
    req = urllib.request.Request(
        "https://form24.es/lote/check/is-ready",
        data=data,
        headers={
            "Referer": "https://form24.es/lote/tie-status",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    resp2 = opener.open(req)
    return json.loads(resp2.read().decode())

TRANSLATIONS = {
    "Tu TIE aún no está lista": "Your TIE is not ready yet",
    "Tu tarjeta aún no está lista.": "Your card is not ready yet.",
    "Tie lista para recoger": "TIE ready for pickup",
    "TIE lista para recoger": "TIE ready for pickup",
    "¡Buenas noticias! Tu tarjeta está lista, puedes recogerla en comisaría.": "Good news! Your card is ready, pick it up at the station.",
    "Buenas noticias! Tu tarjeta está lista, puedes recogerla en comisaría.": "Good news! Your card is ready, pick it up at the station.",
    "Pronto estará listo": "It will be ready soon",
    "TIE lista, puedes recogerla": "TIE ready, you can pick it up",
}

def translate(text):
    if not text:
        return text
    if text in TRANSLATIONS:
        return TRANSLATIONS[text]
    m = re.search(r'faltan\s+(\d+)\s+números?', text)
    if m:
        return f"Status: {m.group(1)} lot(s) to go"
    return text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/offices")
def api_offices():
    return jsonify(OFFICES_DATA)

@app.route("/api/check")
def api_check():
    province = request.args.get("province", "Madrid")
    office = request.args.get("office", "CNP SAN FELIPE TIE, SAN FELIPE, 7")
    office_id = request.args.get("office_id", "143")
    lote = request.args.get("lote", "119")
    year = request.args.get("year", "2026")

    try:
        result = check_tie(province, office, office_id, lote, year)
        flag = result.get("flag_message")
        last_lote = result.get("last_lote", "?")
        my_lote = result.get("client_lote", lote)
        main_msg = translate(result.get("main_message", ""))
        left_msg = translate(result.get("num_left_message", ""))
        queue = result.get("pseudo_que_numbers", "?")

        diff = max(0, int(my_lote) - int(last_lote)) if str(my_lote).isdigit() and str(last_lote).isdigit() else 0
        pct = max(0, min(100, int((int(last_lote) / int(my_lote)) * 100))) if str(my_lote).isdigit() and str(last_lote).isdigit() and int(my_lote) > 0 else 0

        return jsonify({
            "flag": flag,
            "status": "ready" if flag == 3 else "waiting" if flag == 1 else "unknown",
            "my_lote": my_lote,
            "last_lote": last_lote,
            "main_message": main_msg,
            "left_message": left_msg,
            "queue": queue,
            "diff": diff,
            "pct": pct,
            "office": office,
            "checked_at": datetime.now().strftime("%d %b %Y, %H:%M"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

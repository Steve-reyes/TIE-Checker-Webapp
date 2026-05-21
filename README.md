# TIE Checker WebApp 🇵🇭

A web-based status checker for Spanish TIE (Tarjeta de Identidad de Extranjero) collection. Queries **form24.es** to check if your residency card is ready for pickup at your local police station.

Dark mode UI. Dynamic province/office selection. Real-time progress tracking.

## Features

- **52 provinces** with **197 police stations** — pick your comisaría
- **Enter your lote number** — checks against form24.es
- **Status badges** — Ready 🟢 / Waiting ⏳ / Unknown ❓
- **Progress bar** — shows how many lots remain before yours
- **Year selector** — 2025 / 2026
- **Dark theme** — easy on the eyes

## Tech Stack

| Layer | Stack |
|---|---|
| Backend | Python Flask + Gunicorn |
| Frontend | Vanilla JS, HTML, CSS |
| Data | Embedded `offices.json` (52 provinces, 197 offices) |
| Deploy | Docker / Direct |
| Tunneling | Cloudflare Tunnel (trycloudflare.com) |

## How It Works

1. User selects province → office → enters lote number + year
2. Backend scrapes `form24.es/lote/tie-status` with CSRF token + session cookies
3. Returns flag: `3` = ready for pickup, `1` = not yet, other = unknown
4. UI renders status badge, progress bar, and queue info

## Quick Start

```bash
# Direct
pip install flask gunicorn
python3 -m gunicorn --bind 0.0.0.0:5000 app:app

# Docker
docker build -t tie-checker .
docker run -d -p 5000:5000 tie-checker
```

## Author

**dj_steve** 🇵🇭
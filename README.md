# SportStats — AI-Enabled Multi-Sport Performance Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.0+-38B2AC.svg)](https://tailwindcss.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Deploy%20Ready-black.svg)](https://vercel.com/)
[![Tests](https://img.shields.io/badge/Tests-68%20Passed%20(100%25)-brightgreen.svg)](backend/tests/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

SportStats is an AI-enabled multi-sport statistical framework and performance intelligence platform. It unifies, normalizes, and compares athlete and team records across **Football, Basketball, Tennis, and Cricket** into a cohesive, interactive analytical dashboard.

---

## 🌟 Key Features

1. **Dual-Mode Execution Architecture:**
   - **Instant Browser Mode:** Opens directly in any browser (`index.html`) with zero installation, zero compilation, and sub-50ms First Contentful Paint.
   - **Full-Stack Mode:** Asynchronous Python FastAPI backend serving OpenAPI REST endpoints over a structured relational SQLite schema.
2. **Dynamic 6-Axis SVG Radar Comparison Studio:**
   - Trigonometric polar-to-Cartesian coordinate projection projecting athletic performance across 5 functional comparison bases: *All*, *Head-to-Head*, *Offense*, *Defense*, and *Trophies*.
   - Dynamic polygon redrawing and percentile telemetry across 205 cataloged athletes.
3. **Authentic 2026 Live Match Centre:**
   - Real-time international fixtures spanning Cricket (e.g. India vs New Zealand at Seddon Park), UEFA Champions League, NBA, and ATP Masters.
   - Zero-latency sport filtering and interactive match selectors.
4. **Cricket 30-Match Chronology & Cricsheet Scorecards:**
   - Detailed fixture records from 2024 through late 2026 for major cricketing nations.
   - Ball-by-ball Cricsheet ingestion with over-by-over tallies, strike rates, bowling economies, and fall of wickets.
5. **ICC Multi-Gender & Multi-Format Rankings Hub:**
   - Interactive gender switcher (`Men's` / `Women's`) across `Test`, `ODI`, and `T20I` divisions with expandable Top 15 telemetry.
6. **Persistent "My Teams" Studio:**
   - Multi-select favourite teams across individual and team sports with automatic `localStorage` synchronization.
7. **Context-Grounded AI Sports Analyst:**
   - Retrieval-augmented query interface with citation grounding and fallback defenses to prevent hallucination.

---

## 🏗️ Technology Stack

| Layer | Technologies | Key Architectural Decisions |
| :--- | :--- | :--- |
| **Frontend Presentation** | HTML5, Tailwind CSS, Vanilla ECMAScript 2022 | Zero build bloat, instantaneous loading, native SVG vector graphics, full offline capability. |
| **Backend REST API** | Python 3.12, FastAPI, Uvicorn ASGI | Asynchronous non-blocking event loop, Pydantic v2 schemas, automated OpenAPI documentation. |
| **Persistence & Data** | SQLite 3, SQLAlchemy 2.0 ORM, JSON | Sub-millisecond read access, 99:1 read-to-write optimization, zero server DBMS configuration overhead. |
| **Mathematical Engines** | Custom Trigonometric Algorithms, NumPy, Pandas | Normalized percentile scaling ($V_{\text{norm}}$), Win % ($WP$), Net Run Rate ($NRR$), True Shooting % ($TS\%$). |
| **Testing & Quality** | Pytest, Hypothesis, Tag-Depth DOM Parsers | 68 automated unit & integration tests with 100% pass rate. |

---

## 🚀 Quick Start Guide

### Option 1: Instant 1-Click Browser Mode (Zero Setup!)
No Python, no build steps, and no packages required:
1. Double-click `index.html` (or run `run_dashboard.bat` and select `[1]`).
2. The platform opens immediately in your default browser with all client-side telemetry, comparison studios, and live match data active.

### Option 2: Full-Stack FastAPI Backend Mode
To launch the full asynchronous REST backend:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch FastAPI with auto-reload
python -m uvicorn sportstats.api.main:app --app-dir backend/src --host 127.0.0.1 --port 8000 --reload
```
Access the services at:
- **Web Application:** `http://localhost:8000/`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **Health Heartbeat:** `http://localhost:8000/health`

---

## ☁️ Deployment on Vercel

SportStats is configured for native Edge deployment on [Vercel](https://vercel.com):

1. **Connect Repository:** Import this repository into your Vercel Dashboard.
2. **Framework Preset:** Select **Other** (Static Site).
3. **Root Directory:** `./`
4. **Build Command:** Leave default / empty (handled by `vercel.json`).
5. **Output Directory:** `./`
6. Click **Deploy**. Vercel will deploy the application globally across its Edge Network in seconds.

---

## ⚙️ Environment Variables Reference

When running the backend service in production, the following environment variables can be configured:

| Variable Name | Type | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | string | Execution environment (`development`, `staging`, `production`) |
| `DEBUG` | boolean | Enable or disable debug exception tracebacks |
| `PORT` | integer | Server listening port (default: `8000`) |
| `HOST` | string | Server listening host (default: `0.0.0.0`) |
| `DATABASE_URL` | string | SQLAlchemy database connection URI |
| `SECRET_KEY` | string | Cryptographic secret for signing session tokens |
| `ADMIN_API_KEY` | string | API key for administrative endpoints |
| `CORS_ORIGINS` | string | Comma-separated list of allowed CORS origins |
| `LLM_PROVIDER` | string | AI engine provider (`gemini`, `openai`, `mock`) |
| `GEMINI_API_KEY` | string | API token for Gemini AI natural language query interface |
| `ENABLE_LIVE_FEED` | boolean | Toggle live feed background polling |

*(Note: Sensitive values should always be supplied via `.env` or Vercel Environment Variables and never committed to source control.)*

---

## 🧪 Testing & Verification

Run the automated test suite:
```bash
pytest backend/tests/ -q
```
Expected output:
```text
68 passed in 100%
```

---

## 📄 Documentation & Academic Reports

- **Viva Voce & Technical Defense Guide:** `SPORTSTATS_VIVA_AND_PROJECT_GUIDE.pdf` (Top 25 examiner Q&A, mathematical derivations, architecture defense).
- **Academic Project Report:** `SPORTSTATS_PROJECT_REPORT.docx` / `SPORTSTATS_PROJECT_REPORT.md` (16 full-page chapters with figures).
- **Quick Run Guide:** `HOW_TO_RUN.txt`.

---

## 📜 License

This project is licensed under the MIT License — see the LICENSE file for details.

# Z-Code 1.0 — Coding Learning Platform

A full-stack learning platform featuring interactive coding lessons, quizzes, XP & streak tracking, and an AI coding tutor.

---

## 🚀 How to Run

### Step 1: Start the Backend (Terminal 1)

```bash
cd backend
./start.sh
```

- **API Base URL**: `http://localhost:8000/api`
- **Interactive Swagger Docs**: `http://localhost:8000/api/docs`
- **Health Check**: `http://localhost:8000/api/health`

> **Note**: `./start.sh` automatically activates the Python 3.13 virtual environment, seeds the database with initial courses and quizzes, and launches Uvicorn.

---

### Step 2: Open the Frontend (Terminal 2 or Browser)

You can run the frontend in any of these ways:

#### Option A: Quick Open (macOS)
```bash
open Z-Code-Frontend-Starter/login.html
```

#### Option B: Local Web Server (Recommended)
```bash
cd Z-Code-Frontend-Starter
python3 -m http.server 3000
```
Then visit **`http://localhost:3000/login.html`** in your browser.

#### Option C: VS Code Live Server
Right-click `Z-Code-Frontend-Starter/login.html` and click **"Open with Live Server"**.

---

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@zcode.dev` | `admin123` |
| **Demo User** | `dhanush@zcode.dev` | `demo123` |

---

## 📁 Project Structure

- `backend/` — FastAPI backend with SQLite, SQLAlchemy, JWT auth, AI chat (powered by NVIDIA Nemotron 3 Ultra), and quiz validation.
- `Z-Code-Frontend-Starter/` — Web application:
  - `login.html` — User sign in & authentication.
  - `home.html` — Learning dashboard, progress, and AI assistant popup.
  - `python.html` — Python course curriculum with interactive quiz linked to backend XP.
  - `js/api.js` — Client library connecting to backend `/api/chat` with direct NVIDIA AI fallback.

---

## 🤖 NVIDIA Nemotron 3 AI Tutor Integration

Z-Code 1.0 integrates the **NVIDIA Nemotron 3 Ultra 550B** reasoning model (`nvidia/nemotron-3-ultra-550b-a55b`) across both frontend and backend:

1. **Backend Integration**:
   - Configured in `backend/app/config.py` and `backend/.env` via `NVIDIA_API_KEY`, `NVIDIA_BASE_URL`, and `NVIDIA_MODEL`.
   - `backend/app/routers/chat.py` sends user conversation history with reasoning extraction (`enable_thinking=True`).
   - Persists user and assistant messages in the SQLite database.
   - Includes Google Gemini fallback.

2. **Frontend Integration**:
   - In `Z-Code-Frontend-Starter/js/api.js`, `ZCodeAPI.sendChatMessage` routes requests through the backend `/api/chat`.
   - If the backend is running offline or frontend is launched in standalone mode, it automatically falls back to direct client-side NVIDIA NIM API calls.
   - Works across both `home.html` and `python.html` interactive chat drawers.

---

## 🌐 Production Deployment (Vercel + Render)

- **Frontend**: Deployed to **Vercel** with automatic route handling and API proxying via [`vercel.json`](vercel.json).
- **Backend**: Deployed to **Render** with persistent SQLite database via [`render.yaml`](render.yaml).

For step-by-step instructions, see the complete guide: **[DEPLOYMENT.md](DEPLOYMENT.md)**.


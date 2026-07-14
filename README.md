# AI Resume Reviewer

Production-ready resume-vs-job-description analysis app built with a **Next.js frontend** and **FastAPI backend**.
It uploads a resume PDF, parses it, compares it against a job description, computes **deterministic ATS and Match scores**, and then adds a recruiter-style explanation using LLMs.

---

## 🔗 Live Links

| Service | URL |
|---------|-----|
| **Frontend (Vercel)** | https://ai-resume-b39jyq11c-yamunakallakuri-6253s-projects.vercel.app |
| **Backend (LocalTunnel)** | https://nasty-sheep-flash.loca.lt |
| **Backend Health Check** | https://nasty-sheep-flash.loca.lt/health |
| **API Docs (Swagger)** | https://nasty-sheep-flash.loca.lt/docs |

> ⚠️ The backend is currently tunneled via **localtunnel** and runs locally. The tunnel URL may change on restart. Update `BACKEND_URL` on Vercel when it does.

---

## What the app does

- Upload a PDF resume
- Paste a job description
- Extract resume text from the PDF
- Parse and normalize both resume + JD
- Compute deterministic:
  - ATS Score
  - Match Score
  - Score breakdowns
  - Matched / missing / transferable skills
- Generate recruiter-style analysis and rewrite suggestions
- Save the analysis in PostgreSQL

---

## Current Runtime Flow

```mermaid
flowchart LR

    User([👤 User])
    Browser["🌐 Browser"]
    Frontend["⚛️ Next.js Frontend\n(Vercel)"]
    Proxy["🔀 Next.js API Proxy\n/api/v1"]
    Backend["🚀 FastAPI Backend\n(LocalTunnel → localhost:8000)"]
    PDF["📄 Resume PDF Extraction"]
    ATS["🧠 ATS Orchestrator"]
    Score["📊 Deterministic ATS Engine"]
    LLM["🤖 LLM Recruiter Explanation\n+ Audit"]
    DB[("🗄️ PostgreSQL / Supabase")]
    Response["📦 JSON Response"]

    User --> Browser
    Browser --> Frontend
    Frontend --> Proxy
    Proxy --> Backend
    Backend --> PDF
    PDF --> ATS
    ATS --> Score
    Score --> LLM
    LLM --> DB
    LLM --> Response
    Response --> Frontend
    Frontend --> Browser
```

### Important frontend/backend calling detail
The frontend **does not call the backend directly from the browser**.
It uses the Next.js proxy route at:

```
frontend/src/app/api/v1/[...path]/route.ts
```

That proxy forwards requests to the backend using `BACKEND_URL`.

So in production:
- the browser calls **your Vercel frontend**
- the Vercel server forwards to **your localtunnel backend URL**

This means:
- `BACKEND_URL` is the only required frontend deployment variable
- `NEXT_PUBLIC_API_URL` is **not required** for the normal deployed flow

---

## ATS Scoring Flow

Scores are computed by the backend **deterministically first**.
The LLM does **not** decide the ATS or Match score.

```mermaid
flowchart TD
    A[Resume text] --> B[Resume parser]
    C[Job description text] --> D[JD parser]
    B --> E[Skill normalization]
    D --> E
    E --> F[Keyword matcher]
    E --> G[Semantic matcher]
    E --> H[Experience matcher]
    E --> I[Project matcher]
    E --> J[Education matcher]
    E --> K[Formatting analyzer]
    F --> L[Score fusion]
    G --> L
    H --> L
    I --> L
    J --> L
    K --> L
    L --> M[ATS Score + Match Score]
    M --> N[LLM recruiter explanation]
    N --> O[LLM audit pass]
    O --> P[Deterministic validator]
    P --> Q[Saved result + API response]
```

---

## Tech Stack

### Frontend
- Next.js **16**
- React **19**
- TypeScript
- Axios
- Zustand
- Supabase JS client

### Backend
- FastAPI
- Python **3.11**
- SQLAlchemy async + `asyncpg`
- Pydantic v2
- PyMuPDF / OCR fallback
- sentence-transformers
- Groq + Gemini

### Infrastructure
- **Vercel** — Frontend hosting
- **LocalTunnel** — Backend tunnel (development/demo)
- **Supabase** — PostgreSQL database
- **GitHub Actions** — CI/CD

---

## AI Approach

- **Deterministic first**: ATS and Match scores are computed with rule-based + semantic matchers — not by the LLM
- **LLM for explanation only**: Groq/Gemini generates recruiter-style feedback based on the already-computed scores
- **Structured JSON outputs**: All LLM responses are schema-validated before use
- **Graceful fallback**: If LLM fails or returns malformed output, the app still returns deterministic scores without crashing
- **Audit pass**: A second LLM call audits the first response for consistency before returning to the user

---

## Key Trade-offs & Decisions

| Decision | Reason |
|----------|--------|
| Deterministic scoring before LLM | Prevents hallucinated scores; LLM only explains, not decides |
| Next.js proxy instead of direct backend calls | Hides backend URL, centralizes auth headers, avoids CORS issues |
| Groq + Gemini (both) | Groq for speed, Gemini as fallback if Groq fails |
| LocalTunnel for backend | Corporate network blocks all outbound SSH ports; localtunnel works through HTTP |
| Supabase for auth + DB | Handles hashed passwords, JWT, per-user data isolation out of the box |

---

## Repository Structure

```text
AI_Resume/
├── frontend/                     # Next.js app
│   ├── src/app/                  # pages + API proxy route
│   ├── src/lib/axios.ts          # same-origin API client
│   └── next.config.ts
├── backend/                      # FastAPI app
│   ├── app/api/v1/               # API routes
│   ├── app/ats/                  # deterministic ATS engine
│   ├── app/ai/                   # pipeline entrypoint + LLM clients
│   ├── app/services/             # business logic
│   ├── app/models/               # SQLAlchemy models
│   ├── app/prompts/              # recruiter/auditor prompts
│   ├── Dockerfile
│   └── requirements.txt
├── .github/workflows/deploy.yml
├── docker-compose.yml
└── README.md
```

---

## Environment Variables

### Backend (`backend/.env`)

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=resumes
GROQ_API_KEY=your-groq-key
GEMINI_API_KEY=your-gemini-key
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000"]
ENVIRONMENT=development
RATELIMIT_PER_MINUTE=20
LOG_LEVEL=INFO
TESSERACT_CMD=
```

### Frontend (`frontend/.env.local`)

```env
BACKEND_URL=https://nasty-sheep-flash.loca.lt
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

> ⚠️ Update `BACKEND_URL` every time the localtunnel URL changes after a restart.

---

## Local Development Setup

### Prerequisites
- Node.js 20+
- Python 3.11
- Supabase / PostgreSQL database
- Groq API key and/or Gemini API key

### 1) Clone the repo

```bash
git clone <your-repo-url>
cd AI_Resume
```

### 2) Create environment files

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Fill in your real credentials.

### 3) Run the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Windows shortcut:**
```powershell
cd backend
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

### 4) Start localtunnel (to expose backend publicly)

```bash
lt --port 8000 --subdomain airesume
```

This gives you: `https://airesume.loca.lt`

Update `BACKEND_URL` on Vercel with this URL and redeploy.

### 5) Run the frontend

```bash
cd frontend
npm install
npm run dev
```

- Frontend: `http://localhost:3000`
- Backend: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

### 6) Run database migrations

```bash
cd backend
python -m alembic upgrade head
```

---

## Production Deployment

### Deploy order
1. **Supabase / PostgreSQL**
2. **Backend** (locally via localtunnel, or Render)
3. **Frontend** (Vercel)
4. **Update `BACKEND_URL` on Vercel** with backend URL
5. **Smoke test** upload + analyze flow

### Frontend on Vercel

| Variable | Value |
|----------|-------|
| `BACKEND_URL` | `https://nasty-sheep-flash.loca.lt` (update when tunnel restarts) |
| `NEXT_PUBLIC_SUPABASE_URL` | your Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | your Supabase anon key |

### Backend on Render (optional upgrade from localtunnel)

- Root Directory: `backend`
- Start Command:
```bash
sh -c "python -m alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT"
```
- Set all backend env variables in Render dashboard

---

## API Docs

- Swagger UI: https://nasty-sheep-flash.loca.lt/docs
- ReDoc: https://nasty-sheep-flash.loca.lt/redoc
- Health: https://nasty-sheep-flash.loca.lt/health

---

## Summary

| Environment | Frontend | Backend | Database |
|-------------|----------|---------|----------|
| Local | `localhost:3000` | `127.0.0.1:8000` | Supabase |
| Production | Vercel | LocalTunnel → `localhost:8000` | Supabase |

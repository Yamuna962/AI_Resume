# AI Resume Reviewer

Production-ready resume-vs-job-description analysis app built with a **Next.js frontend** and **FastAPI backend**.
It uploads a resume PDF, parses it, compares it against a job description, computes **deterministic ATS and Match scores**, and then adds a recruiter-style explanation using LLMs.

---

## What the app does

- Upload a PDF resume
- Paste a job description
- Extract resume text from the PDF
- Parse and normalize both resume + JD
- Compute deterministic:
  - ATS Score
  - Match Score
  - score breakdowns
  - matched / missing / transferable skills
- Generate recruiter-style analysis and rewrite suggestions
- Save the analysis in PostgreSQL

---

## Current runtime flow

````markdown
## Current Runtime Flow

```mermaid
flowchart LR

    User([👤 User])

    Browser["🌐 Browser"]
    Frontend["⚛️ Next.js Frontend"]

    Proxy["🔀 Next.js API Proxy<br/>/api/v1"]

    Backend["🚀 FastAPI Backend"]

    PDF["📄 Resume PDF Extraction"]

    ATS["🧠 ATS Orchestrator"]

    Score["📊 Deterministic ATS Engine"]

    LLM["🤖 LLM Recruiter Explanation<br/>+ Audit"]

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

### Important frontend/backend calling detail
The frontend **does not call the backend directly from the browser**.
It uses the Next.js proxy route at:

- `frontend/src/app/api/v1/[...path]/route.ts`

That proxy forwards requests to the backend using:

- `BACKEND_URL`

So in production:
- the browser calls **your frontend domain**
- the frontend server forwards to **your backend domain**

This means:
- `BACKEND_URL` is the important frontend deployment variable
- `NEXT_PUBLIC_API_URL` is **not required** for the normal deployed flow

---

## ATS scoring flow

Scores are computed by the backend deterministically first.
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

## Tech stack

### Frontend
- Next.js **16**
- React **19**
- TypeScript
- Axios
- Zustand
- Supabase JS client

### Backend
- FastAPI
- Python **3.11 recommended**
- SQLAlchemy async + `asyncpg`
- Pydantic v2
- PyMuPDF / OCR fallback
- sentence-transformers
- Groq + Gemini

### Infrastructure
- Vercel for frontend
- Render for backend
- Supabase PostgreSQL for database
- GitHub Actions for CI/CD

---

## Repository structure

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

## Environment variables

## Backend (`backend/.env`)

Copy `backend/.env.example` to `backend/.env` and fill in the real values.

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

### Backend variable notes
- `DATABASE_URL`: required
- `SUPABASE_*`: required for current project config
- `JWT_SECRET_KEY`: must be long and random in production
- `CORS_ORIGINS`: JSON array string preferred
- `ENVIRONMENT`: `development`, `testing`, `staging`, or `production`
- `TESSERACT_CMD`: optional; leave blank when `tesseract` is already on your system `PATH`

---

## Frontend (`frontend/.env.local`)

Copy `frontend/.env.local.example` to `frontend/.env.local` and fill in the real values.

```env
BACKEND_URL=http://127.0.0.1:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Frontend variable notes
- `BACKEND_URL`: **required in deployment**, optional locally because the proxy defaults to `http://127.0.0.1:8000`
- `NEXT_PUBLIC_SUPABASE_URL`: required if frontend auth/client code uses Supabase
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: required if frontend auth/client code uses Supabase
- `NEXT_PUBLIC_API_URL`: optional only; not needed for the main deployed flow

---

## Local development

### Prerequisites
- Node.js 20+
- Python 3.11 recommended
- Supabase / PostgreSQL database
- Groq API key and/or Gemini API key

### 1) Clone the repo

```bash
git clone <your-repo-url>
cd AI_Resume
```

### 2) Create environment files

- Copy `backend/.env.example` to `backend/.env`
- Copy `frontend/.env.local.example` to `frontend/.env.local`

Then replace the placeholder values with your real project credentials.

### 3) Install and run the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Windows shortcut
You can also use:

```powershell
cd backend
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

The PowerShell script applies `python -m alembic upgrade head` before starting Uvicorn.

### 4) Install and run the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:
- `http://localhost:3000`

Backend:
- `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

### 5) Database migration behavior
The backend schema is now managed through **Alembic**.
Run this whenever you set up a fresh database or pull a schema change:

```bash
cd backend
python -m alembic upgrade head
```

The initial migration creates the core tables, including `resume_embeddings`.
Because the project uses `pgvector` and `gen_random_uuid()`, make sure your PostgreSQL instance allows the `vector` and `pgcrypto` extensions.

---

## Recommended production deployment

## Deploy order
Deploy in this order:

1. **Supabase / PostgreSQL**
2. **Backend (Render)**
3. **Frontend (Vercel)**
4. **Update CORS and frontend `BACKEND_URL`**
5. **Smoke test upload + analyze flow**

---

## 1) Database / Supabase

Create a Supabase project and get:
- project URL
- anon key
- service role key
- Postgres connection string

Use the Postgres connection string as `DATABASE_URL` in the backend.

> Note: the current scaffold stores a mock `storage_url` for uploaded resumes. You can still create a `resumes` bucket now to stay aligned with config, but backend file upload is currently database-first and not fully storage-backed yet.

---

## 2) Deploy backend to Render

You have two workable paths:

### Option A — Use the existing Dockerfile (recommended)
The repo already includes:
- `backend/Dockerfile`

That Docker image now:
- installs `tesseract-ocr` for scanned PDF fallback
- runs `python -m alembic upgrade head` before starting Uvicorn

On Render:
1. Create a new **Web Service**
2. Connect the GitHub repo
3. Set **Root Directory** to `backend`
4. Choose the Docker deployment path if Render detects the Dockerfile
5. Set environment variables from the backend table above
6. Deploy

### Option B — Use build/start commands
If you prefer command-based deployment on Render:

- Root Directory: `backend`
- Build Command:

```bash
pip install -r requirements.txt
```

- Start Command:

```bash
sh -c "python -m alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT"
```

### Backend production env suggestions

```env
ENVIRONMENT=production
LOG_LEVEL=INFO
ACCESS_TOKEN_EXPIRE_MINUTES=30
RATELIMIT_PER_MINUTE=20
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
```

### Backend health check
Use:

```text
/health
```

Once deployed, note the backend URL, for example:

```text
https://ai-resume-backend.onrender.com
```

---

## 3) Deploy frontend to Vercel

On Vercel:
1. Import the GitHub repo
2. Set **Root Directory** to `frontend`
3. Framework preset: **Next.js**
4. Add environment variables:

```env
BACKEND_URL=https://your-render-backend.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

5. Deploy

### Why `BACKEND_URL` matters
The frontend server route:
- `frontend/src/app/api/v1/[...path]/route.ts`

forwards `/api/v1/*` requests to the backend using `BACKEND_URL`.

So on Vercel, the correct setup is:
- browser → Vercel frontend
- Vercel frontend proxy → Render backend

You usually **do not need** `NEXT_PUBLIC_API_URL` for this production setup.

---

## 4) Production smoke test

After both services are deployed:

1. Open the frontend URL
2. Register / sign in
3. Upload a PDF resume
4. Paste a job description
5. Confirm the request succeeds end-to-end
6. Confirm the backend `/health` endpoint is healthy
7. Confirm scores + explanation render in the frontend

If something fails, check these first:
- `BACKEND_URL` on Vercel
- `DATABASE_URL` on Render
- `CORS_ORIGINS` on Render
- Supabase keys
- Groq / Gemini keys

---

## CI/CD notes

The repo includes:
- `.github/workflows/deploy.yml`

Current workflow behavior:
- backend checks/tests
- frontend typecheck/lint/build
- Vercel deployment on `main`
- Render deploy hook trigger on `main`

If you use that workflow, you will also need the usual GitHub secrets such as:
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_KEY`
- `GROQ_API_KEY`
- `GEMINI_API_KEY`
- `JWT_SECRET_KEY`
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `RENDER_DEPLOY_HOOK_URL`

---

## Notes about Docker Compose

The root `docker-compose.yml` is scaffolding for a fuller local container setup.
However, this repository currently includes:
- `backend/Dockerfile`
- **no committed `frontend/Dockerfile`**

So the documented and supported flow in this README is:
- local dev via `uvicorn` + `npm run dev`
- production deploy via **Render + Vercel**

If you want a fully working all-in Docker local stack, add a `frontend/Dockerfile` first.

---

## API docs

When the backend is running locally:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Summary

### Local flow
- Frontend runs on `localhost:3000`
- Backend runs on `127.0.0.1:8000`
- Frontend proxy forwards `/api/v1/*` to backend

### Production flow
- Frontend on **Vercel**
- Backend on **Render**
- Database on **Supabase**
- Frontend proxy uses `BACKEND_URL` to forward API requests to Render

If you deploy using that flow, your app architecture matches the code exactly.

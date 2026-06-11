# CP Insight — Competitive Programming Analytics Platform

A full-stack web app that connects to a user's **Codeforces** account and turns
their contest and problem-solving history into analytics, weakness detection,
deterministic recommendations, a revision planner, and daily goals.

**Stack:** Django · Django REST Framework · PostgreSQL · JWT auth · Streamlit ·
Pandas · Plotly · Docker.

## 🚀 Live Demo

**App:** https://cpinsight-dashboard.onrender.com
**API:** https://cpinsight-backend.onrender.com/api

> Hosted on Render's free tier, so the first load after a period of inactivity
> takes ~30–60 seconds while the service wakes up. Register an account, connect
> a Codeforces handle (e.g. `tourist`), and the dashboard fills with analytics.

---

## 1. Architecture overview

```
                 ┌──────────────────────┐         ┌──────────────────────┐
   Browser  ───► │  Streamlit dashboard │  HTTP   │   Django REST API    │
                 │  (Plotly charts,     │ ──────► │  (JWT-protected)     │
                 │   session JWT)       │  JSON   │                      │
                 └──────────────────────┘         └──────────┬───────────┘
                                                             │
                                          ┌──────────────────┼──────────────────┐
                                          │                  │                  │
                                   ┌──────▼─────┐   ┌─────────▼────────┐  ┌──────▼──────┐
                                   │ PostgreSQL │   │ Codeforces       │  │ Rule-based  │
                                   │ (all data) │   │ service layer    │  │ analytics   │
                                   └────────────┘   │ (public CF API)  │  │ engine      │
                                                     └──────────────────┘  └─────────────┘
```

- **Backend** owns all data and logic. It is the only component that talks to
  the database and to the Codeforces API (isolated in a *service layer*,
  `codeforces/services.py`).
- **Analytics** (`codeforces/analytics.py`) is 100% deterministic rules — no ML.
- **Dashboard** is a thin client: it logs in, stores the JWT in the Streamlit
  session, calls the API, and draws Plotly charts. It contains no business logic.

### Backend apps
| App | Responsibility |
|-----|----------------|
| `accounts` | Registration, JWT login, profile management |
| `codeforces` | CF data models, API service layer, sync, analytics, recommendations |
| `planner` | Recommendation history, revision tasks, daily goals |

---

## 2. Database schema

```
User (Django built-in)
  └─1:1─ Profile (name, codeforces_handle, current_rating, max_rating, last_synced_at)

User ─1:N─ CodeforcesContest (contest_id, name, rank, old_rating, new_rating, time)
User ─1:N─ UserSolvedProblem ─N:1─ CodeforcesProblem (contest_id, index, name, rating, tags[])
User ─1:N─ TopicStatistics (tag, solved_count)        # derived from solved problems
User ─1:N─ Recommendation (topic, message, created_at)
User ─1:N─ RevisionTask (topic, priority, target_date, status)
User ─1:N─ DailyGoal (description, goal_type, topic, target_count, completed_count, date)
```

`CodeforcesProblem` is a shared global catalog; everything else is per-user.

---

## 3. API endpoints

All `/api/...` endpoints except register/login require an
`Authorization: Bearer <token>` header.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/register/` | Create account |
| POST | `/api/auth/login/` | Get JWT access + refresh tokens |
| POST | `/api/auth/login/refresh/` | Refresh an access token |
| GET/PATCH | `/api/auth/profile/` | View / edit profile |
| POST | `/api/cf/sync/` | Fetch + store CF data for a handle |
| GET | `/api/cf/analytics/overview/` | Rating, contests, total solved |
| GET | `/api/cf/analytics/rating/` | Progression, best rating, avg change |
| GET | `/api/cf/analytics/contests/` | Count by year, avg rank, best rank |
| GET | `/api/cf/analytics/topics/` | Solved per topic, most/least practiced |
| GET | `/api/cf/analytics/weaknesses/` | Rule-based weakness insights |
| POST | `/api/cf/recommend/` | Generate + store recommendations |
| GET | `/api/planner/recommendations/` | Recommendation history |
| CRUD | `/api/planner/revision-tasks/` | Revision tasks (list/create/update/delete) |
| CRUD | `/api/planner/daily-goals/` | Daily goals |

---

## 4. Folder structure

```
cp-insight/
├── backend/
│   ├── cpinsight/            # Django project settings + root urls
│   ├── accounts/             # auth + profile
│   ├── codeforces/           # CF models, services.py, analytics.py, refresh command
│   ├── planner/              # recommendations, revision tasks, daily goals
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── dashboard/
│   ├── Home.py               # entry page (login + overview)
│   ├── api_client.py         # talks to the Django API
│   ├── pages/                # Rating, Topics, Recommendations, Planner, Goals
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 5. Running it — Option A: Docker (recommended)

Requires Docker Desktop.

```bash
docker compose up --build
```

- API:        http://localhost:8000/api/
- Admin:      http://localhost:8000/admin/
- Dashboard:  http://localhost:8501

To create an admin login:
```bash
docker compose exec backend python manage.py createsuperuser
```

## 6. Running it — Option B: locally without Docker

Uses SQLite automatically (no PostgreSQL setup needed) because `DATABASE_URL`
is left empty in `.env`.

**Terminal 1 — backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows  (use: source venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
copy .env.example .env           # Windows  (use: cp .env.example .env elsewhere)
python manage.py migrate
python manage.py runserver
```

**Terminal 2 — dashboard:**
```bash
cd dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

Then open http://localhost:8501, register an account, log in, and enter your
Codeforces handle to sync.

---

## 7. Periodic refresh

Re-sync all stored handles on a schedule (no always-on worker needed):

```bash
python manage.py refresh_codeforces
```

Schedule it with Windows Task Scheduler or cron (e.g. every 6 hours).

---

## 8. Notes for production / deployment

- Set a real `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and a proper
  `DJANGO_ALLOWED_HOSTS`.
- Restrict CORS (`CORS_ALLOW_ALL=False` and configure allowed origins).
- The backend already runs under gunicorn in its Dockerfile.
- Any host that runs Docker (Render, Railway, a VPS, etc.) can run
  `docker compose up`.

---
_Built by itsiftikar02._

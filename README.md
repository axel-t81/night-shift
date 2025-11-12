# Night Shift App

Night Shift App is a Bloomberg Terminal–styled productivity companion built for recurring night-shift study sessions. Track categories, schedule recurring work blocks, and manage every task in a loopable queue—all from a single page backed by a fully documented FastAPI service layer.

## Highlights

- **Recurring block engine** – Complete a block, reset its tasks, and automatically push it to the end of the queue.
- **Bloomberg-inspired UI** – Pure HTML/CSS/vanilla JS with live status, toast notifications, and a focus tracker panel.
- **Full REST API** – 34 endpoints covering categories, blocks, tasks, queue management, and statistics.
- **Cloud-native ready** – Deployable to Cloud Run with PostgreSQL while retaining SQLite for local development.

## Architecture

```
Frontend (index.html + static assets)
        │
FastAPI application (app.main)
        │
Services layer (business logic)
        │
SQLAlchemy models ↔ Database (SQLite or PostgreSQL)
```

Project layout:

```
app/
├── api/        # FastAPI routers
├── services/   # Business logic
├── schemas/    # Pydantic models
├── models/     # SQLAlchemy ORM
├── main.py     # FastAPI entrypoint
└── ...
static/         # CSS, JS
templates/      # index.html
```

## Getting Started

### Prerequisites
- Python 3.11+
- pip / virtualenv (recommended)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize the database
```bash
python init_db.py
```
Creates `night_shift.db` with `categories`, `blocks`, `tasks`, and `quotes` tables. Use SQLite locally; override `DATABASE_URL` for PostgreSQL.

### 3. Run the application
```bash
uvicorn app.main:app --reload
```

Endpoints:
- Web app: `http://localhost:8000/app`
- REST API base: `http://localhost:8000/api`
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

### 4. Optional: preload sample data
Use the interactive docs or `init_db.py` to seed categories, blocks, tasks, and motivational quotes.

## Everyday Workflow

1. Launch the app to see the **Focus Tracker** and the highest-priority block.
2. Expand the block queue, review block details, and manage tasks from the right sidebar.
3. Check/uncheck tasks to record progress; completion timestamps and statistics update instantly.
4. Use **Complete & Reset Block** to roll the block to the end of the queue with all tasks reset.
5. Capture a daily intention in the quote panel and keep distractions in check with the focus tracker.

## Key Features

- Category color coding with task counts
- Real-time block queue with edit/delete shortcuts
- Toast notifications and footer clock
- Bulk and per-task completion API endpoints
- Block cloning, reordering, and statistics
- Focus tracker panel with persistent checklists and celebratory completion flair

## Deployment

Night Shift App runs containerized in Cloud Run with Cloud SQL:

```bash
PROJECT_ID=your-gcp-project
REGION=us-central1
IMAGE=gcr.io/$PROJECT_ID/night-shift-app:$(date +%Y%m%d%H%M)

docker build -t $IMAGE .
docker push $IMAGE

gcloud run deploy night-shift-app \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --add-cloudsql-instances $INSTANCE_CONNECTION_NAME
```

Configure environment variables via Cloud Run (or `.env` locally):

```env
DATABASE_URL=sqlite:///./night_shift.db
# Production example:
# DATABASE_URL=postgresql+pg8000://user:password@/dbname?unix_sock=/cloudsql/project:region:instance/.s.PGSQL.5432
```

## Documentation Suite

- [`FRONTEND_GUIDE.md`](./FRONTEND_GUIDE.md) – Layout, styling system, and UI flows.
- [`API_LAYER_GUIDE.md`](./API_LAYER_GUIDE.md) – Endpoint catalog and usage examples.
- [`SERVICES_LAYER_GUIDE.md`](./SERVICES_LAYER_GUIDE.md) – Business logic and recurring block design.
- Swagger / ReDoc – Self-documenting API references at `/docs` and `/redoc`.

## Maintenance Notes

- The services layer encapsulates all database writes—use it in new endpoints to keep business rules consistent.
- CORS is open for development; restrict `allow_origins` before deploying.
- Run `pytest` (tests folder) before shipping significant API changes.
- Update the focus tracker labels or count via `FOCUS_MODAL_OPTIONS` in `static/js/app.js`.

Night Shift App is production-ready and built for steady, repeatable deep-work sessions. Enjoy the night shift. 🌙

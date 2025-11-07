# Night Shift App

A personal productivity web app for tracking night shift pomodoro blocks and tasks based on Xiaoyu's study plan.

## Tech Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python with FastAPI
- **Database**: SQLite (local) → PostgreSQL (production on Cloud Run)
- **ORM**: SQLAlchemy

## Project Structure

```
app/
├── models/          # SQLAlchemy ORM models (✓ implemented)
├── schemas/         # Pydantic validation schemas (✓ implemented)
├── services/        # Business logic layer
└── api/             # FastAPI routes

static/              # Frontend assets
templates/           # HTML templates
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python init_db.py
```

This creates a SQLite database (`night_shift.db`) with the following tables:
- `categories` - Project/category organization
- `blocks` - Time blocks for pomodoro sessions
- `tasks` - Individual tasks within blocks

### 3. Run the API Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API Base**: `http://localhost:8000/api`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)
- **Health Check**: `http://localhost:8000/health`

### 4. Open the Frontend

Navigate to: `http://localhost:8000/app`

## Behavior Notes

- **Block numbering**: Blocks are numbered sequentially (auto-assigned if not specified).
- **Delete confirmation**: Category deletions use an in-app confirmation modal (no browser dialogs).
- **Quick Actions panel**: Located between Statistics and Categories panels with "+ Add Block" and "+ Add Category" buttons.

## Usage

### First Time Setup

1. **Create Categories** (e.g., "Deep Work", "Learning", "Exercise")
   - Use the "Add Category" button in the sidebar
   - Assign colors for visual organization

2. **Create Blocks** (your work blocks for organizing tasks)
   - Use the "Add Block" button in the Quick Actions panel
   - Set title, optional description, and block_number (for ordering)

3. **Create Tasks** (within blocks)
   - Use the API docs to create tasks
   - Assign to a block and category
   - Set estimated minutes

### Daily Workflow

1. **Open the app** - See your "Next Block" prominently displayed
2. **Complete tasks** - Click checkboxes as you finish each task
3. **Monitor progress** - Watch the progress bar update
4. **Complete block** - When done, click "Complete & Reset Block"
5. **Automatic cycle** - Block moves to end, next block loads automatically
6. **Repeat** - Continue through your night shift! 🌙

## Data Model

### Category
- Organizes tasks by project/topic
- Has name and optional color

### Block
- Category-agnostic container for organizing tasks
- Has title, optional description, block number (ordering), day number (1-5)
- Contains multiple tasks

### Task
- Belongs to one block and one category
- Tracks estimated vs actual minutes
- Has completion status and timestamp
- Position determines order within block

## Services Layer

The services layer provides business logic for recurring blocks:

### Key Features
- **Recurring Blocks**: Blocks can be completed and reset to repeat indefinitely
- **Queue Management**: Blocks ordered by `block_number`, completed blocks move to end
- **Progress Tracking**: Get completion statistics for blocks and categories
- **Block Cloning**: Create copies of blocks with all their tasks

### Core Functions
- `complete_and_reset_block()` - Complete all tasks, reset them, move block to end
- `reset_block_tasks()` - Reset all tasks in a block to incomplete
- `move_block_to_end()` - Move a block to the back of the queue
- `clone_block()` - Create a copy of a block with its tasks

See [SERVICES_LAYER_GUIDE.md](./SERVICES_LAYER_GUIDE.md) for detailed documentation.

## Development Status

- [x] Models Layer - Database schema with SQLAlchemy
- [x] Schemas Layer - Pydantic validation
- [x] Services Layer - Business logic with recurring blocks support
- [x] API Layer - RESTful endpoints (34 endpoints implemented)
- [x] Frontend - Bloomberg Terminal-styled UI (HTML/CSS/JS)

## Documentation

- **[SERVICES_LAYER_GUIDE.md](./SERVICES_LAYER_GUIDE.md)** - Services layer and recurring blocks
- **[API_LAYER_GUIDE.md](./API_LAYER_GUIDE.md)** - API endpoints documentation
- **[FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md)** - Frontend implementation guide

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=sqlite:///./night_shift.db
# For production:
# DATABASE_URL=postgresql://user:password@host:port/dbname
```

### Cloud Run + Cloud SQL Configuration

When deploying to Cloud Run with a Cloud SQL (PostgreSQL) instance, configure the service with the following environment variables:

- `DB_USER` – Database user
- `DB_PASS` – Database password
- `DB_NAME` – Database name
- `INSTANCE_CONNECTION_NAME` – Cloud SQL instance connection name (e.g., `project:region:instance`)
- `DB_SOCKET_DIR` *(optional)* – Defaults to `/cloudsql`; override if you mount the socket elsewhere
- `DB_PORT` *(optional)* – Defaults to `5432`

Alternatively, you can set `DB_HOST` directly to a Unix socket path (e.g., `/cloudsql/project:region:instance`) or provide a full `DATABASE_URL` if you prefer TCP connections.

Remember to enable the Cloud SQL connection on your Cloud Run service (with `--add-cloudsql-instances` or via the console) so the Unix socket becomes available inside the container.


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

## Data Model

### Category
- Organizes tasks by project/topic
- Has name and optional color

### Block
- Category-agnostic time container
- Has start/end time, title, block/day numbers
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
- [ ] Frontend - Bloomberg Terminal-styled UI

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=sqlite:///./night_shift.db
# For production:
# DATABASE_URL=postgresql://user:password@host:port/dbname
```


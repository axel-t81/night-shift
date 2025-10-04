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
├── schemas/         # Pydantic validation schemas
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

## Development Status

- [x] Models Layer - Database schema with SQLAlchemy
- [ ] Schemas Layer - Pydantic validation
- [ ] Services Layer - Business logic (recurring tasks)
- [ ] API Layer - RESTful endpoints
- [ ] Frontend - Bloomberg Terminal-styled UI

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=sqlite:///./night_shift.db
# For production:
# DATABASE_URL=postgresql://user:password@host:port/dbname
```


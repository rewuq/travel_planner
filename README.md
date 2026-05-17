# Travel Planner API

REST API for managing travel projects and places from the [Art Institute of Chicago](https://api.artic.edu/docs/).

## Tech Stack

- **Python 3.12**
- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **SQLite** — database
- **httpx** — HTTP client for AIC API

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/rewuq/travel_planner.git
cd travel_planner
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

---

## API Documentation

Once the app is running, open one of these in your browser:

- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc

---

## Endpoints

### Projects

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/projects/` | Create a project (optionally with places) |
| `GET` | `/projects/` | List all projects |
| `GET` | `/projects/{id}` | Get a single project with its places |
| `PATCH` | `/projects/{id}` | Update project name / description / start date |
| `DELETE` | `/projects/{id}` | Delete a project |

### Places

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/projects/{id}/places/` | Add a place to a project |
| `GET` | `/projects/{id}/places/` | List all places in a project |
| `GET` | `/projects/{id}/places/{place_id}` | Get a single place |
| `PATCH` | `/projects/{id}/places/{place_id}` | Update notes or mark as visited |

---

## Example Requests

### Create a project without places

```bash
curl -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicago Trip",
    "description": "Art museums tour",
    "start_date": "2025-06-01"
  }'
```

### Create a project with places

```bash
curl -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicago Trip",
    "places": [
      {"external_id": 27992},
      {"external_id": 28560}
    ]
  }'
```

> `external_id` is the artwork ID from the [Art Institute of Chicago API](https://api.artic.edu/api/v1/artworks).  
> You can browse artworks at `https://api.artic.edu/api/v1/artworks` to find valid IDs.

### Add a place to an existing project

```bash
curl -X POST http://localhost:8000/projects/1/places/ \
  -H "Content-Type: application/json" \
  -d '{"external_id": 27992}'
```

### Update notes for a place

```bash
curl -X PATCH http://localhost:8000/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{"notes": "Must see the original frame up close"}'
```

### Mark a place as visited

```bash
curl -X PATCH http://localhost:8000/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{"visited": true}'
```

> When **all places** in a project are marked as visited, the project status automatically changes to `completed`.

### Delete a project

```bash
curl -X DELETE http://localhost:8000/projects/1
```

> A project **cannot** be deleted if any of its places are already marked as visited.

---

## Business Rules

- A project can have **1 to 10 places**
- The same artwork cannot be added to the same project twice
- A place is validated against the AIC API before being saved
- Deleting a project with visited places returns `400 Bad Request`
- When all places are visited, the project status changes to `completed` automatically

---

## Project Structure

```
travel_planner/
├── main.py          # FastAPI app entry point
├── database.py      # SQLAlchemy engine and session
├── models.py        # ORM models (Project, Place)
├── schemas.py       # Pydantic schemas for validation
├── crud.py          # Database operations
├── requirements.txt
├── routers/
│   ├── projects.py  # Project endpoints
│   └── places.py    # Place endpoints
└── services/
    └── artic.py     # Art Institute of Chicago API client
```
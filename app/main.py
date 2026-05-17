"""
Точка входу FastAPI додатку.

Запуск:
    uvicorn main:app --reload

Документація:
    http://localhost:8000/docs      (Swagger UI)
    http://localhost:8000/redoc     (ReDoc)
"""

from fastapi import FastAPI
from database import init_db
from routers import projects, places

app = FastAPI(
    title="Travel Planner API",
    description=(
        "API для планування подорожей. "
        "Дозволяє створювати проєкти, додавати місця з Art Institute of Chicago, "
        "вести нотатки та відмічати відвідані місця."
    ),
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    """Створює таблиці в БД при старті якщо вони ще не існують."""
    init_db()


# Підключаємо роутери
app.include_router(projects.router)
app.include_router(places.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Travel Planner API is running"}
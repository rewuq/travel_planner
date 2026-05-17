"""
Роутер для місць в межах проєкту.

Endpoints:
    POST   /projects/{id}/places              — додати місце до проєкту
    GET    /projects/{id}/places              — список місць проєкту
    GET    /projects/{id}/places/{place_id}   — одне місце
    PATCH  /projects/{id}/places/{place_id}   — оновити notes / visited
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import PlaceCreate, PlaceUpdate, PlaceResponse
from services.artic import validate_artwork_exists

router = APIRouter(
    prefix="/projects/{project_id}/places",
    tags=["Places"],
)


@router.post(
    "/",
    response_model=PlaceResponse,
    status_code=201,
    summary="Додати місце до проєкту",
    description=(
        "Додає нове місце до існуючого проєкту. "
        "Перевіряє існування external_id в Art Institute of Chicago API. "
        "Максимум 10 місць на проєкт."
    ),
)
def add_place(
    project_id: int,
    payload: PlaceCreate,
    db: Session = Depends(get_db),
):
    # Валідація: перевіряємо що експонат існує в AIC API
    artwork = validate_artwork_exists(payload.external_id)  # кидає 422 якщо не знайдено
    title = artwork.get("title")

    return crud.add_place_to_project(
        db=db,
        project_id=project_id,
        external_id=payload.external_id,
        title=title,
    )


@router.get(
    "/",
    response_model=list[PlaceResponse],
    summary="Список місць проєкту",
    description="Повертає всі місця для вказаного проєкту.",
)
def list_places(project_id: int, db: Session = Depends(get_db)):
    return crud.get_all_places(db=db, project_id=project_id)


@router.get(
    "/{place_id}",
    response_model=PlaceResponse,
    summary="Отримати місце",
    description="Повертає одне місце в межах проєкту.",
)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    return crud.get_place(db=db, project_id=project_id, place_id=place_id)


@router.patch(
    "/{place_id}",
    response_model=PlaceResponse,
    summary="Оновити місце",
    description=(
        "Оновлює нотатки або статус visited для місця. "
        "Якщо всі місця проєкту стають visited — проєкт автоматично позначається як completed."
    ),
)
def update_place(
    project_id: int,
    place_id: int,
    payload: PlaceUpdate,
    db: Session = Depends(get_db),
):
    return crud.update_place(
        db=db,
        project_id=project_id,
        place_id=place_id,
        notes=payload.notes,
        visited=payload.visited,
    )
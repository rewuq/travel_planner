"""
Роутер для проєктів подорожей.

Endpoints:
    POST   /projects               — створити проєкт (+ опційно місця)
    GET    /projects               — список проєктів
    GET    /projects/{id}          — один проєкт з місцями
    PATCH  /projects/{id}          — оновити проєкт
    DELETE /projects/{id}          — видалити проєкт
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithPlacesResponse,
    MessageResponse,
)
from services.artic import validate_artwork_exists

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/",
    response_model=ProjectWithPlacesResponse,
    status_code=201,
    summary="Створити проєкт",
    description="Створює новий проєкт. Можна одразу передати список місць (external_id з AIC API).",
)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    # 1. Якщо передані місця — валідуємо кожне в AIC API ДО запису в БД
    validated_places = []
    if payload.places:
        for place in payload.places:
            artwork = validate_artwork_exists(place.external_id)
            validated_places.append({
                "external_id": place.external_id,
                "title": artwork.get("title"),
            })

    # 2. Створюємо проєкт
    project = crud.create_project(
        db=db,
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )

    # 3. Додаємо валідовані місця
    for place_data in validated_places:
        crud.add_place_to_project(
            db=db,
            project_id=project.id,
            external_id=place_data["external_id"],
            title=place_data["title"],
        )

    # 4. Оновлюємо об'єкт щоб підтягнути places
    db.refresh(project)
    return project


@router.get(
    "/",
    response_model=list[ProjectResponse],
    summary="Список проєктів",
    description="Повертає список всіх проєктів.",
)
def list_projects(db: Session = Depends(get_db)):
    return crud.get_all_projects(db=db)


@router.get(
    "/{project_id}",
    response_model=ProjectWithPlacesResponse,
    summary="Отримати проєкт",
    description="Повертає один проєкт разом зі списком його місць.",
)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return crud.get_project(db=db, project_id=project_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Оновити проєкт",
    description="Оновлює назву, опис або дату початку проєкту. Передавай тільки ті поля які треба змінити.",
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
):
    return crud.update_project(
        db=db,
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )


@router.delete(
    "/{project_id}",
    response_model=MessageResponse,
    summary="Видалити проєкт",
    description="Видаляє проєкт. Неможливо видалити якщо хоча б одне місце вже відвідане.",
)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    return crud.delete_project(db=db, project_id=project_id)
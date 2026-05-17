"""
CRUD операції для Travel Planner.

Кожна функція приймає db: Session як перший аргумент —
це сесія SQLAlchemy, яку FastAPI передає через Depends(get_db).
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from models import Project, Place


# ---------------------------------------------------------------------------
# PROJECT CRUD
# ---------------------------------------------------------------------------

def get_project(db: Session, project_id: int) -> Project:
    """Повертає проєкт за ID або кидає 404."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id={project_id} not found"
        )
    return project


def get_all_projects(db: Session) -> list[Project]:
    """Повертає список всіх проєктів."""
    return db.query(Project).all()


def create_project(
    db: Session,
    name: str,
    description: str | None = None,
    start_date=None
) -> Project:
    """Створює новий проєкт."""
    project = Project(name=name, description=description, start_date=start_date)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session,
    project_id: int,
    name: str | None = None,
    description: str | None = None,
    start_date=None
) -> Project:
    """Оновлює поля проєкту. Передавай тільки ті поля, які треба змінити."""
    project = get_project(db, project_id)

    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    if start_date is not None:
        project.start_date = start_date

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> dict:
    """
    Видаляє проєкт.
    Заборонено видаляти проєкт, якщо хоча б одне місце вже відвідане.
    """
    project = get_project(db, project_id)

    has_visited = db.query(Place).filter(
        and_(Place.project_id == project_id, Place.visited == True)
    ).first()

    if has_visited:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project with visited places"
        )

    db.delete(project)
    db.commit()
    return {"detail": f"Project {project_id} deleted successfully"}


# ---------------------------------------------------------------------------
# PLACE CRUD
# ---------------------------------------------------------------------------

def get_place(db: Session, project_id: int, place_id: int) -> Place:
    """Повертає місце за ID в межах проєкту або кидає 404."""
    place = db.query(Place).filter(
        and_(Place.id == place_id, Place.project_id == project_id)
    ).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Place with id={place_id} not found in project {project_id}"
        )
    return place


def get_all_places(db: Session, project_id: int) -> list[Place]:
    """Повертає всі місця для конкретного проєкту."""
    get_project(db, project_id)
    return db.query(Place).filter(Place.project_id == project_id).all()


def add_place_to_project(
    db: Session,
    project_id: int,
    external_id: int,
    title: str | None = None
) -> Place:
    """
    Додає нове місце до проєкту.

    Перевірки:
    1. Проєкт існує
    2. Не більше 10 місць у проєкті
    3. Це місце ще не додане до цього проєкту
    """
    get_project(db, project_id)

    current_count = db.query(Place).filter(Place.project_id == project_id).count()
    if current_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project already has the maximum of 10 places"
        )

    duplicate = db.query(Place).filter(
        and_(Place.project_id == project_id, Place.external_id == external_id)
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Place with external_id={external_id} already exists in this project"
        )

    place = Place(project_id=project_id, external_id=external_id, title=title)
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


def update_place(
    db: Session,
    project_id: int,
    place_id: int,
    notes: str | None = None,
    visited: bool | None = None
) -> Place:
    """
    Оновлює notes та/або visited для місця.
    Якщо всі місця проєкту стають visited — проєкт автоматично позначається completed.
    """
    place = get_place(db, project_id, place_id)

    if notes is not None:
        place.notes = notes

    if visited is not None:
        place.visited = visited

        all_places = db.query(Place).filter(Place.project_id == project_id).all()
        all_visited = all(p.visited for p in all_places)

        project = db.query(Project).filter(Project.id == project_id).first()
        project.status = "completed" if all_visited else "active"

    db.commit()
    db.refresh(place)
    return place
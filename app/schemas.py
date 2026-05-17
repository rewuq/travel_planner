"""
Pydantic схеми для валідації запитів та відповідей.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# PLACE SCHEMAS
# ---------------------------------------------------------------------------

class PlaceBase(BaseModel):
    external_id: int = Field(..., description="ID експоната з Art Institute of Chicago API")


class PlaceCreate(PlaceBase):
    """Схема для додавання місця до проєкту."""
    pass


class PlaceUpdate(BaseModel):
    """Всі поля optional — можна передати тільки те, що треба змінити."""
    notes: Optional[str] = Field(None, max_length=2000, description="Нотатки до місця")
    visited: Optional[bool] = Field(None, description="Відмітити місце як відвідане")


class PlaceResponse(BaseModel):
    """Схема відповіді для одного місця."""
    id: int
    project_id: int
    external_id: int
    title: Optional[str] = None
    notes: Optional[str] = None
    visited: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# PROJECT SCHEMAS
# ---------------------------------------------------------------------------

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Назва проєкту")
    description: Optional[str] = Field(None, max_length=1000, description="Опис проєкту")
    start_date: Optional[date] = Field(None, description="Дата початку подорожі")


class ProjectCreate(ProjectBase):
    """
    Схема для створення проєкту.
    Можна одразу передати список місць (external_id з AIC API).
    """
    places: Optional[list[PlaceCreate]] = Field(
        None,
        min_length=1,
        max_length=10,
        description="Список місць для додавання при створенні проєкту"
    )

    @field_validator("places")
    @classmethod
    def validate_unique_places(cls, places):
        """Перевіряємо що в запиті немає дублікатів external_id."""
        if places is None:
            return places
        ids = [p.external_id for p in places]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate external_id values in places list")
        return places


class ProjectUpdate(BaseModel):
    """Всі поля optional — можна передати тільки те, що треба змінити."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None


class ProjectResponse(ProjectBase):
    """Схема відповіді для одного проєкту (без списку місць)."""
    id: int
    status: str

    model_config = {"from_attributes": True}


class ProjectWithPlacesResponse(ProjectResponse):
    """Схема відповіді для проєкту разом зі списком його місць."""
    places: list[PlaceResponse] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ЗАГАЛЬНІ СХЕМИ
# ---------------------------------------------------------------------------

class MessageResponse(BaseModel):
    """Проста відповідь з повідомленням (наприклад, при видаленні)."""
    detail: str
from datetime import datetime, date
from typing import Optional
from sqlalchemy import Integer, String, Text, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Project(Base):
    """
    Таблиця travel_projects — зберігає інформацію про проєкти подорожей.

    Статуси:
    - 'active'    — є невідвідані місця
    - 'completed' — всі місця помічені як visited
    """
    __tablename__ = "travel_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    

    places: Mapped[list["Place"]] = relationship(
        "Place", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project id={self.id} name={self.name!r} status={self.status!r}>"


class Place(Base):
    """
    Таблиця project_places — зберігає місця (експонати AIC) в межах проєкту.

    external_id — ID експоната з Art Institute of Chicago API.
    Поєднання (project_id + external_id) повинно бути унікальним,
    щоб не можна було додати один і той самий експонат двічі.
    """
    __tablename__ = "project_places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("travel_projects.id", ondelete="CASCADE"), nullable=False
    )
    external_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


    project: Mapped["Project"] = relationship("Project", back_populates="places")

    def __repr__(self):
        return (
            f"<Place id={self.id} external_id={self.external_id} "
            f"visited={self.visited} project_id={self.project_id}>"
        )
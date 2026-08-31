from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    mission_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    spacecraft_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    mission_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    modality: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    event: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    mission_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    modality: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    anomaly_type: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class FusionEvent(Base):
    __tablename__ = "fusion_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    mission_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    anomaly_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    multi_modal_agreement: Mapped[bool] = mapped_column(
        default=False,
    )

    anomalous_modalities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
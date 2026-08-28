from datetime import datetime

from pydantic import BaseModel, Field


class MissionState(BaseModel):
    mission_id: str
    timestamp: datetime

    status: str = "NOMINAL"

    risk_score: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Overall mission risk score",
    )

    active_anomalies: list[str] = Field(
        default_factory=list,
        description="Currently detected anomalies",
    )

    affected_systems: list[str] = Field(
        default_factory=list,
        description="Spacecraft or mission systems affected by anomalies",
    )

    evidence: list[str] = Field(
        default_factory=list,
        description="Evidence contributing to the current mission assessment",
    )

    recommended_actions: list[str] = Field(
        default_factory=list,
        description="Actions recommended by the decision system",
    )

    summary: str | None = Field(
        default=None,
        description="Human-readable summary of the current mission state",
    )
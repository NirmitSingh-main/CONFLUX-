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
        description="Overall mission risk score"
    )

    active_anomalies: list[str] = Field(default_factory=list)

    affected_systems: list[str] = Field(default_factory=list)

    summary: str | None = None
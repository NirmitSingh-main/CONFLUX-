from datetime import datetime

from pydantic import BaseModel, Field


class MissionState(BaseModel):
    """
    Represents the current operational state of a mission.
    """

    mission_id: str
    timestamp: datetime

    status: str = "NOMINAL"

    active_events: list[str] = Field(
        default_factory=list,
        description="Currently active mission events",
    )

    active_anomalies: list[str] = Field(
        default_factory=list,
        description="Currently detected anomalies",
    )

    affected_systems: list[str] = Field(
        default_factory=list,
        description="Spacecraft systems affected by active events",
    )

    priorities: dict[str, str] = Field(
        default_factory=dict,
        description="Operational priority assigned to active events",
    )

    conflicts: list[str] = Field(
        default_factory=list,
        description="Detected conflicts between mission events",
    )

    summary: str | None = Field(
        default=None,
        description="Human-readable summary of the current mission state",
    )
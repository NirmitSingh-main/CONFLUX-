from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import (
    Observation,
    AnomalyEvent,
)
from backend.models.orbital import (
    OrbitalState,
    Vector3D,
)
from backend.physics.conjunction import assess_conjunction
from backend.intelligence.orbital_risk import (
    OrbitalRiskAnalyzer,
)


router = APIRouter()


# --------------------------------------------------
# Request models
# --------------------------------------------------

class OrbitalObjectInput(BaseModel):
    object_id: str
    timestamp: datetime

    position: Vector3D
    velocity: Vector3D


class OrbitalAnalysisInput(BaseModel):
    mission_id: int

    object1: OrbitalObjectInput
    object2: OrbitalObjectInput

    safety_distance: float = 1.0


# --------------------------------------------------
# Analyzer
# --------------------------------------------------

risk_analyzer = OrbitalRiskAnalyzer()


# --------------------------------------------------
# Orbital analysis endpoint
# --------------------------------------------------

@router.post("/")
def analyze_orbital(
    request: OrbitalAnalysisInput,
    db: Session = Depends(get_db),
):

    # Convert request data into OrbitalState objects.

    state1 = OrbitalState(
        object_id=request.object1.object_id,
        timestamp=request.object1.timestamp,
        position=request.object1.position,
        velocity=request.object1.velocity,
    )

    state2 = OrbitalState(
        object_id=request.object2.object_id,
        timestamp=request.object2.timestamp,
        position=request.object2.position,
        velocity=request.object2.velocity,
    )

    # ------------------------------------------------
    # Physics layer
    # ------------------------------------------------

    conjunction = assess_conjunction(
        state1,
        state2,
        safety_distance=request.safety_distance,
    )

    # ------------------------------------------------
    # Intelligence layer
    # ------------------------------------------------

    result = risk_analyzer.analyze(
        conjunction
    )

    # ------------------------------------------------
    # Store observation
    # ------------------------------------------------

    observation = Observation(
        mission_id=request.mission_id,
        modality="orbital",
        value=result["miss_distance"],
        event=result["event_type"],
    )

    db.add(observation)

    # ------------------------------------------------
    # Store anomaly when orbital situation is
    # WARNING or CRITICAL.
    # ------------------------------------------------

    if result["status"] in {
        "WARNING",
        "CRITICAL",
    }:

        anomaly = AnomalyEvent(
            mission_id=request.mission_id,
            modality="orbital",
            anomaly_type=result["event_type"],
            description=(
                f"Orbital conjunction between "
                f"{result['object1_id']} and "
                f"{result['object2_id']}. "
                f"Miss distance: "
                f"{result['miss_distance']:.4f} km."
            ),
        )

        db.add(anomaly)

    db.commit()

    # ------------------------------------------------
    # Return result
    # ------------------------------------------------

    return {
        "mission_id": request.mission_id,
        "modality": "orbital",

        "object1_id": result["object1_id"],
        "object2_id": result["object2_id"],

        "current_distance": result["current_distance"],
        "relative_speed": conjunction.relative_speed,

        "time_to_closest_approach":
            result["time_to_closest_approach"],

        "miss_distance":
            result["miss_distance"],

        "collision_risk":
            result["collision_risk"],

        "status":
            result["status"],

        "event_type":
            result["event_type"],

        "risk_level":
            conjunction.risk_level,

        "stored_in_database": True,
    }
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import (
    Observation,
    AnomalyEvent,
    OrbitalAnalysis,
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

    result = risk_analyzer.analyze(conjunction)

    # ------------------------------------------------
    # Compute confidence (deterministic: physics-based)
    # Orbital analysis is always high-confidence since
    # it is a deterministic geometric calculation.
    # ------------------------------------------------

    confidence = 0.95

    # ------------------------------------------------
    # Persist to structured analysis table
    # ------------------------------------------------

    analysis_record = OrbitalAnalysis(
        mission_id=request.mission_id,
        object1_id=result["object1_id"],
        object2_id=result["object2_id"],
        primary_position_x=request.object1.position.x,
        primary_position_y=request.object1.position.y,
        primary_position_z=request.object1.position.z,
        primary_velocity_x=request.object1.velocity.x,
        primary_velocity_y=request.object1.velocity.y,
        primary_velocity_z=request.object1.velocity.z,
        secondary_position_x=request.object2.position.x,
        secondary_position_y=request.object2.position.y,
        secondary_position_z=request.object2.position.z,
        secondary_velocity_x=request.object2.velocity.x,
        secondary_velocity_y=request.object2.velocity.y,
        secondary_velocity_z=request.object2.velocity.z,
        safety_threshold=request.safety_distance,
        current_distance=result["current_distance"],
        miss_distance=result["miss_distance"],
        relative_speed=conjunction.relative_speed,
        time_to_closest_approach=result["time_to_closest_approach"],
        event_type=result["event_type"],
        status=result["status"],
        risk_level=conjunction.risk_level,
        collision_risk=result["collision_risk"],
        confidence=confidence,
    )

    db.add(analysis_record)

    # ------------------------------------------------
    # Also store legacy generic observation record
    # ------------------------------------------------

    observation = Observation(
        mission_id=request.mission_id,
        modality="orbital",
        value=result["miss_distance"],
        event=result["event_type"],
    )
    db.add(observation)

    # ------------------------------------------------
    # Store legacy anomaly event when WARNING or CRITICAL
    # ------------------------------------------------

    if result["status"] in {"WARNING", "CRITICAL"}:
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
    db.refresh(analysis_record)

    # ------------------------------------------------
    # Return result
    # ------------------------------------------------

    return {
        "id": analysis_record.id,
        "mission_id": request.mission_id,
        "modality": "orbital",

        "object1_id": result["object1_id"],
        "object2_id": result["object2_id"],

        "current_distance": result["current_distance"],
        "relative_speed": conjunction.relative_speed,

        "time_to_closest_approach": result["time_to_closest_approach"],
        "miss_distance": result["miss_distance"],
        "safety_threshold": request.safety_distance,

        "collision_risk": result["collision_risk"],
        "status": result["status"],
        "event_type": result["event_type"],
        "risk_level": conjunction.risk_level,

        "confidence": confidence,
        "stored_in_database": True,
    }


# --------------------------------------------------
# GET latest orbital analysis for a mission
# --------------------------------------------------

@router.get("/latest/{mission_id}")
def get_latest_orbital(
    mission_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(OrbitalAnalysis)
        .filter(OrbitalAnalysis.mission_id == mission_id)
        .order_by(OrbitalAnalysis.created_at.desc())
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No orbital analysis found for mission {mission_id}",
        )

    return {
        "id": record.id,
        "mission_id": record.mission_id,
        "modality": "orbital",
        "object1_id": record.object1_id,
        "object2_id": record.object2_id,
        "current_distance": record.current_distance,
        "relative_speed": record.relative_speed,
        "time_to_closest_approach": record.time_to_closest_approach,
        "miss_distance": record.miss_distance,
        "safety_threshold": record.safety_threshold,
        "collision_risk": record.collision_risk,
        "status": record.status,
        "event_type": record.event_type,
        "risk_level": record.risk_level,
        "confidence": record.confidence,
        "created_at": record.created_at.isoformat(),
    }

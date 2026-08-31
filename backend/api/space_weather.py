import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import (
    Observation,
    AnomalyEvent,
    SpaceWeatherAnalysis,
)
from backend.intelligence.space_weather import (
    SpaceWeatherAnalyzer,
)


router = APIRouter()


# --------------------------------------------------
# Request model
# --------------------------------------------------

class SpaceWeatherInput(BaseModel):
    mission_id: int

    solar_activity: float
    radiation_level: float
    geomagnetic_activity: float


# --------------------------------------------------
# Analyzer
# --------------------------------------------------

analyzer = SpaceWeatherAnalyzer(
    solar_activity_threshold=492.545,
    radiation_threshold=7.749,
    geomagnetic_activity_threshold=3.565,
)


def _compute_severity(active_event_count: int) -> str:
    """Compute overall severity from number of active events."""
    if active_event_count == 0:
        return "LOW"
    elif active_event_count == 1:
        return "MEDIUM"
    else:
        return "HIGH"


def _compute_overall_status(environmental_anomaly: bool) -> str:
    if environmental_anomaly:
        return "ENVIRONMENTAL_ANOMALY"
    return "NOMINAL"


def _compute_confidence(solar_activity: float, radiation_level: float, geomagnetic_activity: float) -> float:
    """
    Confidence is high for space-weather analysis because all inputs
    are measured values compared against fixed thresholds.
    """
    # All three inputs are valid positive numbers; threshold comparisons
    # are deterministic. Fixed at 0.90.
    return 0.90


# --------------------------------------------------
# Space-weather analysis endpoint
# --------------------------------------------------

@router.post("/")
def analyze_space_weather(
    request: SpaceWeatherInput,
    db: Session = Depends(get_db),
):
    # Analyze the measured environmental conditions.
    result = analyzer.analyze(
        solar_activity=request.solar_activity,
        radiation_level=request.radiation_level,
        geomagnetic_activity=request.geomagnetic_activity,
    )

    severity = _compute_severity(len(result["active_events"]))
    overall_status = _compute_overall_status(result["environmental_anomaly"])
    confidence = _compute_confidence(
        request.solar_activity,
        request.radiation_level,
        request.geomagnetic_activity,
    )

    # ------------------------------------------------
    # Persist to structured analysis table
    # ------------------------------------------------

    analysis_record = SpaceWeatherAnalysis(
        mission_id=request.mission_id,
        solar_activity=request.solar_activity,
        radiation_level=request.radiation_level,
        geomagnetic_activity=request.geomagnetic_activity,
        solar_event=result["solar_event"],
        radiation_event=result["radiation_event"],
        geomagnetic_event=result["geomagnetic_event"],
        active_events=json.dumps(result["active_events"]),
        environmental_anomaly=result["environmental_anomaly"],
        overall_status=overall_status,
        severity=severity,
        confidence=confidence,
    )

    db.add(analysis_record)

    # ------------------------------------------------
    # Legacy generic observation record
    # ------------------------------------------------

    observation = Observation(
        mission_id=request.mission_id,
        modality="space_weather",
        value=request.radiation_level,
        event=(
            ", ".join(result["active_events"])
            if result["active_events"]
            else "NO_SIGNIFICANT_SPACE_WEATHER_EVENT"
        ),
    )
    db.add(observation)

    # ------------------------------------------------
    # Legacy anomaly event
    # ------------------------------------------------

    if result["environmental_anomaly"]:
        anomaly = AnomalyEvent(
            mission_id=request.mission_id,
            modality="space_weather",
            anomaly_type=", ".join(result["active_events"]),
            description="Elevated space-weather activity detected from environmental measurements.",
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
        "modality": "space_weather",

        "solar_activity": result["solar_activity"],
        "radiation_level": result["radiation_level"],
        "geomagnetic_activity": result["geomagnetic_activity"],

        "solar_event": result["solar_event"],
        "radiation_event": result["radiation_event"],
        "geomagnetic_event": result["geomagnetic_event"],

        # active_events is authoritative; do not return both booleans
        # AND the list — the frontend must use only active_events.
        "active_events": result["active_events"],

        "environmental_anomaly": result["environmental_anomaly"],
        "overall_status": overall_status,
        "severity": severity,
        "confidence": confidence,

        "stored_in_database": True,
    }


# --------------------------------------------------
# GET latest space weather analysis for a mission
# --------------------------------------------------

@router.get("/latest/{mission_id}")
def get_latest_space_weather(
    mission_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(SpaceWeatherAnalysis)
        .filter(SpaceWeatherAnalysis.mission_id == mission_id)
        .order_by(SpaceWeatherAnalysis.created_at.desc())
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No space weather analysis found for mission {mission_id}",
        )

    active_events = []
    if record.active_events:
        try:
            active_events = json.loads(record.active_events)
        except Exception:
            active_events = [e.strip() for e in record.active_events.split(",") if e.strip()]

    return {
        "id": record.id,
        "mission_id": record.mission_id,
        "modality": "space_weather",
        "solar_activity": record.solar_activity,
        "radiation_level": record.radiation_level,
        "geomagnetic_activity": record.geomagnetic_activity,
        "solar_event": record.solar_event,
        "radiation_event": record.radiation_event,
        "geomagnetic_event": record.geomagnetic_event,
        "active_events": active_events,
        "environmental_anomaly": record.environmental_anomaly,
        "overall_status": record.overall_status,
        "severity": record.severity,
        "confidence": record.confidence,
        "created_at": record.created_at.isoformat(),
    }

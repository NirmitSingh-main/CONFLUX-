import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import (
    FusionAnalysis,
    OrbitalAnalysis,
    SpaceWeatherAnalysis,
    TelemetryAnalysis,
    ThermalAnalysis,
    WavefrontAnalysis,
    Mission,
)
from backend.intelligence.multimodal_fusion import MultimodalFusion


router = APIRouter()
fusion_engine = MultimodalFusion()


# --------------------------------------------------
# Request model
# --------------------------------------------------

class FusionRequest(BaseModel):
    mission_id: int
    # Which modalities to include. If None or empty → include all available.
    modalities: list[str] | None = None


# --------------------------------------------------
# Helper: load latest analysis records from DB
# --------------------------------------------------

def _load_orbital(mission_id: int, db: Session) -> dict | None:
    record = (
        db.query(OrbitalAnalysis)
        .filter(OrbitalAnalysis.mission_id == mission_id)
        .order_by(OrbitalAnalysis.created_at.desc())
        .first()
    )
    if record is None:
        return None
    return {
        "id": record.id,
        "modality": "orbital",
        "object1_id": record.object1_id,
        "object2_id": record.object2_id,
        "current_distance": record.current_distance,
        "miss_distance": record.miss_distance,
        "relative_speed": record.relative_speed,
        "time_to_closest_approach": record.time_to_closest_approach,
        "event_type": record.event_type,
        "status": record.status,
        "risk_level": record.risk_level,
        "collision_risk": record.collision_risk,
        "confidence": record.confidence,
        "safety_threshold": record.safety_threshold,
        "created_at": record.created_at.isoformat(),
    }


def _load_space_weather(mission_id: int, db: Session) -> dict | None:
    record = (
        db.query(SpaceWeatherAnalysis)
        .filter(SpaceWeatherAnalysis.mission_id == mission_id)
        .order_by(SpaceWeatherAnalysis.created_at.desc())
        .first()
    )
    if record is None:
        return None
    active_events: list = []
    if record.active_events:
        try:
            active_events = json.loads(record.active_events)
        except Exception:
            active_events = [e.strip() for e in record.active_events.split(",") if e.strip()]
    return {
        "id": record.id,
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
        "status": record.overall_status,  # alias for fusion engine
        "severity": record.severity,
        "confidence": record.confidence,
        "created_at": record.created_at.isoformat(),
    }


def _load_telemetry(mission_id: int, db: Session) -> dict | None:
    record = (
        db.query(TelemetryAnalysis)
        .filter(TelemetryAnalysis.mission_id == mission_id)
        .order_by(TelemetryAnalysis.created_at.desc())
        .first()
    )
    if record is None:
        return None
    return {
        "id": record.id,
        "modality": "telemetry",
        "measurements": {
            "temperature": record.temperature,
            "voltage": record.voltage,
            "current": record.current,
            "battery": record.battery,
            "pressure": record.pressure,
            "vibration": record.vibration,
        },
        "anomaly_detected": record.anomaly_detected,
        "decision_value": record.decision_value,
        "severity": record.severity,
        "confidence": record.confidence,
        "status": record.status,
        "created_at": record.created_at.isoformat(),
    }


def _load_thermal(mission_id: int, db: Session) -> dict | None:
    record = (
        db.query(ThermalAnalysis)
        .filter(ThermalAnalysis.mission_id == mission_id)
        .order_by(ThermalAnalysis.created_at.desc())
        .first()
    )
    if record is None:
        return None
    return {
        "id": record.id,
        "modality": "thermal",
        "filename": record.filename,
        "anomaly_detected": record.anomaly_detected,
        "hotspot_ratio": record.hotspot_ratio,
        "hotspot_pixels": record.hotspot_pixels,
        "severity": record.severity,
        "confidence": record.confidence,
        "status": record.status,
        "created_at": record.created_at.isoformat(),
    }


def _load_wavefront(mission_id: int, db: Session) -> dict | None:
    record = (
        db.query(WavefrontAnalysis)
        .filter(WavefrontAnalysis.mission_id == mission_id)
        .order_by(WavefrontAnalysis.created_at.desc())
        .first()
    )
    if record is None:
        return None
    return {
        "id": record.id,
        "modality": "wavefront",
        "anomaly_detected": record.anomaly_detected,
        "anomaly_score": record.anomaly_score,
        "max_z_score": record.max_z_score,
        "energy_ratio": record.energy_ratio,
        "wavelet_anomaly": record.wavelet_anomaly,
        "severity": record.severity,
        "confidence": record.confidence,
        "status": record.status,
        "created_at": record.created_at.isoformat(),
    }


# --------------------------------------------------
# POST /fusion/ — Run fusion from persisted DB analyses
# --------------------------------------------------

@router.post("/")
def run_fusion(
    request: FusionRequest,
    db: Session = Depends(get_db),
):
    # Validate that the mission exists
    mission = db.query(Mission).filter(Mission.id == request.mission_id).first()
    if mission is None:
        raise HTTPException(
            status_code=404,
            detail=f"Mission {request.mission_id} not found.",
        )

    # Determine which modalities to include. Canonicalize legacy aliases so
    # the API accepts both "wavefront" and "wavelet" but stores the canonical
    # name consistently in the DB-driven fusion result.
    requested_raw = set(request.modalities or [])
    requested = set()
    for item in requested_raw:
        key = str(item).strip().lower()
        if key == "wavelet":
            key = "wavefront"
        requested.add(key)

    if not requested:
        requested = {"orbital", "space_weather", "telemetry", "thermal", "wavefront"}

    # Load latest analyses from the database
    orbital = _load_orbital(request.mission_id, db) if "orbital" in requested else None
    space_weather = _load_space_weather(request.mission_id, db) if "space_weather" in requested else None
    telemetry = _load_telemetry(request.mission_id, db) if "telemetry" in requested else None
    thermal = _load_thermal(request.mission_id, db) if "thermal" in requested else None
    wavefront = _load_wavefront(request.mission_id, db) if "wavefront" in requested else None

    # Check that at least one analysis is available
    if all(v is None for v in [orbital, space_weather, telemetry, thermal, wavefront]):
        raise HTTPException(
            status_code=422,
            detail=(
                f"No analysis data found for mission {request.mission_id}. "
                "Run at least one modality analysis before requesting fusion."
            ),
        )

    # Run fusion engine
    fusion_result = fusion_engine.fuse(
        telemetry=telemetry,
        thermal=thermal,
        wavefront=wavefront,
        orbital=orbital,
        space_weather=space_weather,
    )

    # ------------------------------------------------
    # Persist fusion analysis to database
    # ------------------------------------------------

    fusion_record = FusionAnalysis(
        mission_id=request.mission_id,
        orbital_analysis_id=orbital["id"] if orbital else None,
        space_weather_analysis_id=space_weather["id"] if space_weather else None,
        telemetry_analysis_id=telemetry["id"] if telemetry else None,
        thermal_analysis_id=thermal["id"] if thermal else None,
        wavefront_analysis_id=wavefront["id"] if wavefront else None,
        available_modalities=",".join(fusion_result["available_modalities"]),
        anomalous_modalities=",".join(fusion_result["anomalous_modalities"]),
        normal_modalities=",".join(fusion_result["normal_modalities"]),
        unavailable_modalities=",".join(fusion_result["unavailable_modalities"]),
        anomaly_count=fusion_result["anomaly_count"],
        multi_modal_agreement=fusion_result["multi_modal_agreement"],
        correlated_events=json.dumps(fusion_result["correlated_events"]),
        primary_problem=fusion_result["primary_problem"],
        overall_severity=fusion_result["overall_severity"],
        risk_level=fusion_result["risk_level"],
        confidence=fusion_result["confidence"],
        explanation=fusion_result["explanation"],
        recommended_action=fusion_result["recommended_action"],
    )

    db.add(fusion_record)
    db.commit()
    db.refresh(fusion_record)

    # ------------------------------------------------
    # Build per-modality detail summaries for response
    # ------------------------------------------------

    modality_details: dict = {}
    for name, data in [
        ("orbital", orbital),
        ("space_weather", space_weather),
        ("telemetry", telemetry),
        ("thermal", thermal),
        ("wavefront", wavefront),
    ]:
        if data is not None:
            modality_details[name] = {
                "analysis_id": data.get("id"),
                "status": data.get("status", "UNKNOWN"),
                "anomaly_detected": name in fusion_result["anomalous_modalities"],
                "severity": data.get("severity", "UNKNOWN"),
                "confidence": data.get("confidence", 0.75),
                "created_at": data.get("created_at"),
            }
        else:
            modality_details[name] = {"status": "ANALYSIS_UNAVAILABLE"}

    return {
        "id": fusion_record.id,
        "mission_id": request.mission_id,
        "mission_name": mission.mission_name,
        "spacecraft_name": mission.spacecraft_name,

        # Modality breakdown
        "available_modalities": fusion_result["available_modalities"],
        "unavailable_modalities": fusion_result["unavailable_modalities"],
        "anomalous_modalities": fusion_result["anomalous_modalities"],
        "normal_modalities": fusion_result["normal_modalities"],
        "anomaly_count": fusion_result["anomaly_count"],
        "multi_modal_agreement": fusion_result["multi_modal_agreement"],

        # Per-modality summaries (from DB records — NOT frontend state)
        "modality_details": modality_details,
        "modality_states": fusion_result["modality_states"],

        # Cross-modal analysis
        "correlated_events": fusion_result["correlated_events"],
        "primary_problem": fusion_result["primary_problem"],

        # Overall assessment
        "overall_severity": fusion_result["overall_severity"],
        "risk_level": fusion_result["risk_level"],
        "confidence": fusion_result["confidence"],
        "explanation": fusion_result["explanation"],
        "recommended_action": fusion_result["recommended_action"],

        "stored_in_database": True,
        "created_at": fusion_record.created_at.isoformat(),
    }


# --------------------------------------------------
# GET /fusion/latest/{mission_id} — Retrieve last fusion
# --------------------------------------------------

@router.get("/latest/{mission_id}")
def get_latest_fusion(
    mission_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(FusionAnalysis)
        .filter(FusionAnalysis.mission_id == mission_id)
        .order_by(FusionAnalysis.created_at.desc())
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No fusion analysis found for mission {mission_id}",
        )

    correlated_events: list = []
    if record.correlated_events:
        try:
            correlated_events = json.loads(record.correlated_events)
        except Exception:
            correlated_events = []

    return {
        "id": record.id,
        "mission_id": record.mission_id,
        "available_modalities": [m for m in (record.available_modalities or "").split(",") if m],
        "unavailable_modalities": [m for m in (record.unavailable_modalities or "").split(",") if m],
        "anomalous_modalities": [m for m in (record.anomalous_modalities or "").split(",") if m],
        "normal_modalities": [m for m in (record.normal_modalities or "").split(",") if m],
        "anomaly_count": record.anomaly_count,
        "multi_modal_agreement": record.multi_modal_agreement,
        "correlated_events": correlated_events,
        "primary_problem": record.primary_problem,
        "overall_severity": record.overall_severity,
        "risk_level": record.risk_level,
        "confidence": record.confidence,
        "explanation": record.explanation,
        "recommended_action": record.recommended_action,
        "created_at": record.created_at.isoformat(),
    }

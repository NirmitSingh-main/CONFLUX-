from pathlib import Path
import sys

import joblib
import numpy as np

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session


sys.path.append(
    str(Path(__file__).resolve().parents[2])
)


from backend.database.database import get_db
from backend.database.models import (
    Observation,
    AnomalyEvent,
    TelemetryAnalysis,
)


router = APIRouter()


# --------------------------------------------------
# Load trained telemetry model
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "telemetry_isolation_forest.joblib"
)


if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Telemetry model not found: {MODEL_PATH}"
    )


telemetry_model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# Telemetry input
# --------------------------------------------------

class TelemetryInput(BaseModel):
    mission_id: int

    temperature: float
    voltage: float
    current: float

    battery: float
    pressure: float
    vibration: float


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def _compute_severity(anomaly_detected: bool, decision_value: float) -> str:
    """
    Severity based on how far the decision value falls into the anomaly
    region. The IsolationForest decision_function returns negative scores
    for anomalies; more negative = more anomalous.
    """
    if not anomaly_detected:
        return "LOW"
    if decision_value < -0.3:
        return "HIGH"
    return "MEDIUM"


def _compute_confidence(decision_value: float) -> float:
    """
    Confidence based on the magnitude of the decision boundary offset.
    Further from 0 = higher confidence in the prediction.
    """
    # Map |decision_value| to [0.5, 0.99]
    magnitude = min(abs(decision_value) * 5.0, 0.99)
    return round(max(0.50, min(0.99, magnitude)), 2)


# --------------------------------------------------
# Analyze telemetry
# --------------------------------------------------

@router.post("/")
def analyze_telemetry(
    telemetry: TelemetryInput,
    db: Session = Depends(get_db),
):

    # IMPORTANT:
    # This order MUST remain identical to
    # the order used during model training.

    features = np.array(
        [[
            telemetry.temperature,
            telemetry.voltage,
            telemetry.current,
            telemetry.battery,
            telemetry.pressure,
            telemetry.vibration,
        ]],
        dtype=float,
    )

    # ------------------------------------------------
    # ML prediction
    # ------------------------------------------------

    prediction = telemetry_model.predict(features)[0]
    anomaly_detected = (int(prediction) == -1)

    decision_value = float(
        telemetry_model.decision_function(features)[0]
    )

    severity = _compute_severity(anomaly_detected, decision_value)
    confidence = _compute_confidence(decision_value)
    status = "ANOMALOUS" if anomaly_detected else "NOMINAL"

    # ------------------------------------------------
    # Persist to structured analysis table
    # ------------------------------------------------

    analysis_record = TelemetryAnalysis(
        mission_id=telemetry.mission_id,
        temperature=telemetry.temperature,
        voltage=telemetry.voltage,
        current=telemetry.current,
        battery=telemetry.battery,
        pressure=telemetry.pressure,
        vibration=telemetry.vibration,
        anomaly_detected=anomaly_detected,
        model_output=int(prediction),
        decision_value=decision_value,
        severity=severity,
        confidence=confidence,
        status=status,
    )

    db.add(analysis_record)

    # ------------------------------------------------
    # Legacy generic observations
    # ------------------------------------------------

    observations = [
        Observation(mission_id=telemetry.mission_id, modality="telemetry", value=telemetry.temperature, event="temperature"),
        Observation(mission_id=telemetry.mission_id, modality="telemetry", value=telemetry.voltage, event="voltage"),
        Observation(mission_id=telemetry.mission_id, modality="telemetry", value=telemetry.current, event="current"),
        Observation(mission_id=telemetry.mission_id, modality="telemetry", value=telemetry.battery, event="battery"),
        Observation(mission_id=telemetry.mission_id, modality="telemetry", value=telemetry.pressure, event="pressure"),
        Observation(mission_id=telemetry.mission_id, modality="telemetry", value=telemetry.vibration, event="vibration"),
    ]
    db.add_all(observations)

    # ------------------------------------------------
    # Legacy anomaly event
    # ------------------------------------------------

    if anomaly_detected:
        anomaly = AnomalyEvent(
            mission_id=telemetry.mission_id,
            modality="telemetry",
            anomaly_type="TELEMETRY_ANOMALY",
            description="Isolation Forest detected anomalous telemetry.",
        )
        db.add(anomaly)

    db.commit()
    db.refresh(analysis_record)

    # ------------------------------------------------
    # Response
    # ------------------------------------------------

    return {
        "id": analysis_record.id,
        "mission_id": telemetry.mission_id,
        "modality": "telemetry",

        "measurements": {
            "temperature": telemetry.temperature,
            "voltage": telemetry.voltage,
            "current": telemetry.current,
            "battery": telemetry.battery,
            "pressure": telemetry.pressure,
            "vibration": telemetry.vibration,
        },

        "anomaly_detected": anomaly_detected,
        "model_output": int(prediction),
        "decision_value": decision_value,

        "severity": severity,
        "confidence": confidence,
        "status": status,

        "stored_in_database": True,
    }


# --------------------------------------------------
# GET latest telemetry analysis for a mission
# --------------------------------------------------

@router.get("/latest/{mission_id}")
def get_latest_telemetry(
    mission_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(TelemetryAnalysis)
        .filter(TelemetryAnalysis.mission_id == mission_id)
        .order_by(TelemetryAnalysis.created_at.desc())
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No telemetry analysis found for mission {mission_id}",
        )

    return {
        "id": record.id,
        "mission_id": record.mission_id,
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
        "model_output": record.model_output,
        "decision_value": record.decision_value,
        "severity": record.severity,
        "confidence": record.confidence,
        "status": record.status,
        "created_at": record.created_at.isoformat(),
    }

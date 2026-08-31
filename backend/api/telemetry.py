from pathlib import Path
import sys

import joblib
import numpy as np

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session


sys.path.append(
    str(Path(__file__).resolve().parents[2])
)


from backend.database.database import get_db
from backend.database.models import (
    Observation,
    AnomalyEvent,
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


telemetry_model = joblib.load(
    MODEL_PATH
)


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

    prediction = telemetry_model.predict(
        features
    )[0]

    anomaly_detected = (
        int(prediction) == -1
    )

    decision_value = float(
        telemetry_model.decision_function(
            features
        )[0]
    )

    # ------------------------------------------------
    # Store observations
    # ------------------------------------------------

    observations = [
        Observation(
            mission_id=telemetry.mission_id,
            modality="telemetry",
            value=telemetry.temperature,
            event="temperature",
        ),
        Observation(
            mission_id=telemetry.mission_id,
            modality="telemetry",
            value=telemetry.voltage,
            event="voltage",
        ),
        Observation(
            mission_id=telemetry.mission_id,
            modality="telemetry",
            value=telemetry.current,
            event="current",
        ),
        Observation(
            mission_id=telemetry.mission_id,
            modality="telemetry",
            value=telemetry.battery,
            event="battery",
        ),
        Observation(
            mission_id=telemetry.mission_id,
            modality="telemetry",
            value=telemetry.pressure,
            event="pressure",
        ),
        Observation(
            mission_id=telemetry.mission_id,
            modality="telemetry",
            value=telemetry.vibration,
            event="vibration",
        ),
    ]

    db.add_all(observations)

    # ------------------------------------------------
    # Store anomaly event
    # ------------------------------------------------

    if anomaly_detected:

        anomaly = AnomalyEvent(
            mission_id=telemetry.mission_id,
            modality="telemetry",
            anomaly_type="TELEMETRY_ANOMALY",
            description=(
                "Isolation Forest detected "
                "anomalous telemetry."
            ),
        )

        db.add(anomaly)

    db.commit()

    # ------------------------------------------------
    # Response
    # ------------------------------------------------

    return {
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

        "stored_in_database": True,
    }
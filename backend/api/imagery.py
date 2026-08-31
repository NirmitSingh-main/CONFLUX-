from pathlib import Path
import sys

import cv2
import numpy as np

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session


sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from backend.database.database import get_db
from backend.database.models import (
    Observation,
    AnomalyEvent,
)
from backend.intelligence.thermal_anomaly import (
    ThermalAnomalyDetector,
)


router = APIRouter()


# --------------------------------------------------
# Thermal anomaly detector
# --------------------------------------------------

thermal_detector = ThermalAnomalyDetector(
    threshold_factor=2.5,
    hotspot_ratio_threshold=0.01,
)


# --------------------------------------------------
# Analyze infrared image
# --------------------------------------------------

@router.post("/")
async def analyze_imagery(
    mission_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # ------------------------------------------------
    # Read uploaded image
    # ------------------------------------------------

    image_bytes = await file.read()

    if not image_bytes:
        raise ValueError(
            "Uploaded image is empty."
        )

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError(
            "Uploaded file is not a valid image."
        )

    # ------------------------------------------------
    # Run thermal anomaly detection
    # ------------------------------------------------

    result = thermal_detector.detect(
        image
    )

    anomaly_detected = bool(
        result["anomaly_detected"]
    )

    # ------------------------------------------------
    # Store thermal observation
    # ------------------------------------------------

    observation = Observation(
        mission_id=mission_id,
        modality="thermal",
        value=result["hottest_intensity"],
        event="THERMAL_ANALYSIS",
    )

    db.add(observation)

    # ------------------------------------------------
    # Store anomaly event
    # ------------------------------------------------

    if anomaly_detected:

        anomaly = AnomalyEvent(
            mission_id=mission_id,
            modality="thermal",
            anomaly_type="THERMAL_ANOMALY",
            description=(
                f"Thermal hotspot detected. "
                f"Hotspot ratio: "
                f"{result['hotspot_ratio']:.4f}"
            ),
        )

        db.add(anomaly)

    db.commit()

    # ------------------------------------------------
    # Return analysis
    # ------------------------------------------------

    return {
        "mission_id": mission_id,
        "modality": "thermal",

        "filename": file.filename,

        "anomaly_detected": anomaly_detected,

        "mean_intensity":
            result["mean_intensity"],

        "standard_deviation":
            result["standard_deviation"],

        "threshold":
            result["threshold"],

        "hottest_intensity":
            result["hottest_intensity"],

        "hottest_location":
            result["hottest_location"],

        "hotspot_pixels":
            result["hotspot_pixels"],

        "hotspot_ratio":
            result["hotspot_ratio"],

        "stored_in_database": True,
    }
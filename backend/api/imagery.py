from pathlib import Path
import sys

import cv2
import numpy as np

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session


sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from backend.database.database import get_db
from backend.database.models import (
    Observation,
    AnomalyEvent,
    ThermalAnalysis,
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
# Helpers
# --------------------------------------------------

def _compute_severity(anomaly_detected: bool, hotspot_ratio: float) -> str:
    if not anomaly_detected:
        return "LOW"
    if hotspot_ratio > 0.10:
        return "HIGH"
    if hotspot_ratio > 0.03:
        return "MEDIUM"
    return "LOW"


def _compute_confidence(anomaly_detected: bool, hotspot_ratio: float, hotspot_pixels: int) -> float:
    """
    Confidence based on hotspot signal strength.
    More pixels and higher ratio = higher confidence.
    """
    if not anomaly_detected:
        return round(min(0.99, 0.80 + hotspot_ratio * 2.0), 2)
    # For detected anomalies, more hotspot pixels = higher confidence
    pixel_factor = min(hotspot_pixels / 200.0, 0.20)
    ratio_factor = min(hotspot_ratio * 5.0, 0.20)
    return round(min(0.99, 0.60 + pixel_factor + ratio_factor), 2)


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
        raise ValueError("Uploaded image is empty.")

    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Uploaded file is not a valid image.")

    # ------------------------------------------------
    # Run thermal anomaly detection
    # ------------------------------------------------

    result = thermal_detector.detect(image)

    anomaly_detected = bool(result["anomaly_detected"])
    hotspot_ratio = float(result["hotspot_ratio"])
    hotspot_pixels = int(result["hotspot_pixels"])

    severity = _compute_severity(anomaly_detected, hotspot_ratio)
    confidence = _compute_confidence(anomaly_detected, hotspot_ratio, hotspot_pixels)
    status = "ANOMALOUS" if anomaly_detected else "NOMINAL"

    # ------------------------------------------------
    # Persist to structured analysis table
    # ------------------------------------------------

    analysis_record = ThermalAnalysis(
        mission_id=mission_id,
        filename=file.filename,
        mean_intensity=float(result["mean_intensity"]),
        standard_deviation=float(result["standard_deviation"]),
        threshold=float(result["threshold"]),
        hottest_intensity=float(result["hottest_intensity"]),
        hotspot_pixels=hotspot_pixels,
        hotspot_ratio=hotspot_ratio,
        anomaly_detected=anomaly_detected,
        severity=severity,
        confidence=confidence,
        status=status,
    )

    db.add(analysis_record)

    # ------------------------------------------------
    # Legacy generic observation
    # ------------------------------------------------

    observation = Observation(
        mission_id=mission_id,
        modality="thermal",
        value=result["hottest_intensity"],
        event="THERMAL_ANALYSIS",
    )
    db.add(observation)

    # ------------------------------------------------
    # Legacy anomaly event
    # ------------------------------------------------

    if anomaly_detected:
        anomaly = AnomalyEvent(
            mission_id=mission_id,
            modality="thermal",
            anomaly_type="THERMAL_ANOMALY",
            description=(
                f"Thermal hotspot detected. "
                f"Hotspot ratio: {result['hotspot_ratio']:.4f}"
            ),
        )
        db.add(anomaly)

    db.commit()
    db.refresh(analysis_record)

    # ------------------------------------------------
    # Return analysis
    # ------------------------------------------------

    return {
        "id": analysis_record.id,
        "mission_id": mission_id,
        "modality": "thermal",

        "filename": file.filename,

        "anomaly_detected": anomaly_detected,

        "mean_intensity": result["mean_intensity"],
        "standard_deviation": result["standard_deviation"],
        "threshold": result["threshold"],
        "hottest_intensity": result["hottest_intensity"],
        "hottest_location": result["hottest_location"],
        "hotspot_pixels": hotspot_pixels,
        "hotspot_ratio": hotspot_ratio,

        "severity": severity,
        "confidence": confidence,
        "status": status,

        "stored_in_database": True,
    }


# --------------------------------------------------
# GET latest thermal analysis for a mission
# --------------------------------------------------

@router.get("/latest/{mission_id}")
def get_latest_thermal(
    mission_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(ThermalAnalysis)
        .filter(ThermalAnalysis.mission_id == mission_id)
        .order_by(ThermalAnalysis.created_at.desc())
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No thermal analysis found for mission {mission_id}",
        )

    return {
        "id": record.id,
        "mission_id": record.mission_id,
        "modality": "thermal",
        "filename": record.filename,
        "anomaly_detected": record.anomaly_detected,
        "mean_intensity": record.mean_intensity,
        "standard_deviation": record.standard_deviation,
        "threshold": record.threshold,
        "hottest_intensity": record.hottest_intensity,
        "hotspot_pixels": record.hotspot_pixels,
        "hotspot_ratio": record.hotspot_ratio,
        "severity": record.severity,
        "confidence": record.confidence,
        "status": record.status,
        "created_at": record.created_at.isoformat(),
    }

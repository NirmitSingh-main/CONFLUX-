from pathlib import Path
import sys
import joblib
import numpy as np

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import Observation, AnomalyEvent, WavefrontAnalysis


router = APIRouter()


# --------------------------------------------------
# Request model
# --------------------------------------------------

class WavefrontAnalysisInput(BaseModel):
    mission_id: int

    wavefront_rms_um: float
    tip_error_um: float
    tilt_error_um: float
    defocus_um: float
    astigmatism_um: float
    coma_um: float

    # Optional RMS time-series for wavelet analysis.
    signal: list[float] | None = None


# --------------------------------------------------
# Load trained detector
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "wavefront_detector.pkl"
)

wavefront_model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def _compute_severity(anomaly_detected: bool, anomaly_score: float) -> str:
    if not anomaly_detected:
        return "LOW"
    if anomaly_score > 2.0:
        return "HIGH"
    if anomaly_score > 1.0:
        return "MEDIUM"
    return "LOW"


def _compute_confidence(anomaly_score: float, max_z_score: float) -> float:
    """
    Confidence based on both the aggregate anomaly score and the max z-score.
    Higher deviations = higher confidence in the detection.
    """
    score_factor = min(anomaly_score / 3.0, 0.30)
    z_factor = min(max_z_score / 10.0, 0.20)
    base = 0.55
    return round(min(0.99, base + score_factor + z_factor), 2)


# --------------------------------------------------
# Wavefront analysis endpoint
# --------------------------------------------------

@router.post("/")
def analyze_wavefront(
    request: WavefrontAnalysisInput,
    db: Session = Depends(get_db),
):

    # --------------------------------------------------
    # Build the six features in the exact order
    # expected by WavefrontAnomalyDetector.
    # --------------------------------------------------

    features = np.array(
        [
            request.wavefront_rms_um,
            request.tip_error_um,
            request.tilt_error_um,
            request.defocus_um,
            request.astigmatism_um,
            request.coma_um,
        ],
        dtype=float,
    )

    # --------------------------------------------------
    # Optional wavelet signal
    # --------------------------------------------------

    signal = None
    if request.signal is not None:
        signal = np.array(request.signal, dtype=float)

    # --------------------------------------------------
    # Run trained wavefront detector
    # --------------------------------------------------

    result = wavefront_model.analyze(
        features=features,
        signal=signal,
    )

    anomaly_score = float(result["anomaly_score"])
    max_z_score = float(result["max_z_score"])
    anomaly_detected = bool(result["anomaly_detected"])

    severity = _compute_severity(anomaly_detected, anomaly_score)
    confidence = _compute_confidence(anomaly_score, max_z_score)
    status = "ANOMALOUS" if anomaly_detected else "NOMINAL"

    # --------------------------------------------------
    # Persist to structured analysis table
    # --------------------------------------------------

    analysis_record = WavefrontAnalysis(
        mission_id=request.mission_id,
        wavefront_rms_um=request.wavefront_rms_um,
        tip_error_um=request.tip_error_um,
        tilt_error_um=request.tilt_error_um,
        defocus_um=request.defocus_um,
        astigmatism_um=request.astigmatism_um,
        coma_um=request.coma_um,
        anomaly_detected=anomaly_detected,
        anomaly_score=anomaly_score,
        max_z_score=max_z_score,
        energy_ratio=float(result["energy_ratio"]),
        wavelet_anomaly=bool(result["wavelet_anomaly"]),
        severity=severity,
        confidence=confidence,
        status=status,
    )

    db.add(analysis_record)

    # --------------------------------------------------
    # Legacy generic observation
    # --------------------------------------------------

    observation = Observation(
        mission_id=request.mission_id,
        modality="wavelet",
        value=anomaly_score,
        event=(
            "WAVEFRONT_ANOMALY"
            if anomaly_detected
            else "NORMAL_WAVEFRONT"
        ),
    )
    db.add(observation)

    # --------------------------------------------------
    # Legacy anomaly event
    # --------------------------------------------------

    if anomaly_detected:
        anomaly = AnomalyEvent(
            mission_id=request.mission_id,
            modality="wavelet",
            anomaly_type="WAVEFRONT_ANOMALY",
            description=(
                "Wavefront anomaly detected. "
                f"Maximum z-score: {max_z_score:.4f}. "
                f"Energy ratio: {result['energy_ratio']:.4f}."
            ),
        )
        db.add(anomaly)

    db.commit()
    db.refresh(analysis_record)

    # --------------------------------------------------
    # Return analysis
    # --------------------------------------------------

    return {
        "id": analysis_record.id,
        "mission_id": request.mission_id,
        "modality": "wavelet",

        "anomaly_detected": anomaly_detected,
        "anomaly_score": anomaly_score,
        "max_z_score": max_z_score,

        "feature_scores": result["feature_scores"],

        "wavelet_energy": result["wavelet_energy"],
        "baseline_energy": result["baseline_energy"],
        "energy_ratio": result["energy_ratio"],
        "wavelet_anomaly": result["wavelet_anomaly"],
        "wavelet": result["wavelet"],
        "level": result["level"],

        "severity": severity,
        "confidence": confidence,
        "status": status,

        "stored_in_database": True,
    }


# --------------------------------------------------
# GET latest wavefront analysis for a mission
# --------------------------------------------------

@router.get("/latest/{mission_id}")
def get_latest_wavefront(
    mission_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(WavefrontAnalysis)
        .filter(WavefrontAnalysis.mission_id == mission_id)
        .order_by(WavefrontAnalysis.created_at.desc())
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No wavefront analysis found for mission {mission_id}",
        )

    return {
        "id": record.id,
        "mission_id": record.mission_id,
        "modality": "wavefront",
        "wavefront_rms_um": record.wavefront_rms_um,
        "tip_error_um": record.tip_error_um,
        "tilt_error_um": record.tilt_error_um,
        "defocus_um": record.defocus_um,
        "astigmatism_um": record.astigmatism_um,
        "coma_um": record.coma_um,
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

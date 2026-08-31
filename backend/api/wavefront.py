from pathlib import Path
import sys
import joblib
import numpy as np

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import Observation, AnomalyEvent


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
        signal = np.array(
            request.signal,
            dtype=float,
        )

    # --------------------------------------------------
    # Run trained wavefront detector
    # --------------------------------------------------

    result = wavefront_model.analyze(
        features=features,
        signal=signal,
    )

    # --------------------------------------------------
    # Store main observation
    # --------------------------------------------------

    observation = Observation(
        mission_id=request.mission_id,
        modality="wavelet",
        value=result["anomaly_score"],
        event=(
            "WAVEFRONT_ANOMALY"
            if result["anomaly_detected"]
            else "NORMAL_WAVEFRONT"
        ),
    )

    db.add(observation)

    # --------------------------------------------------
    # Store anomaly event
    # --------------------------------------------------

    if result["anomaly_detected"]:

        anomaly = AnomalyEvent(
            mission_id=request.mission_id,
            modality="wavelet",
            anomaly_type="WAVEFRONT_ANOMALY",
            description=(
                "Wavefront anomaly detected. "
                f"Maximum z-score: "
                f"{result['max_z_score']:.4f}. "
                f"Energy ratio: "
                f"{result['energy_ratio']:.4f}."
            ),
        )

        db.add(anomaly)

    db.commit()

    # --------------------------------------------------
    # Return analysis
    # --------------------------------------------------

    return {
        "mission_id": request.mission_id,
        "modality": "wavelet",

        "anomaly_detected": result[
            "anomaly_detected"
        ],

        "anomaly_score": result[
            "anomaly_score"
        ],

        "max_z_score": result[
            "max_z_score"
        ],

        "feature_scores": result[
            "feature_scores"
        ],

        "wavelet_energy": result[
            "wavelet_energy"
        ],

        "baseline_energy": result[
            "baseline_energy"
        ],

        "energy_ratio": result[
            "energy_ratio"
        ],

        "wavelet_anomaly": result[
            "wavelet_anomaly"
        ],

        "wavelet": result[
            "wavelet"
        ],

        "level": result[
            "level"
        ],

        "stored_in_database": True,
    }
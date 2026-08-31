from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import FusionEvent
from backend.intelligence.multimodal_fusion import MultimodalFusion


router = APIRouter()

fusion = MultimodalFusion()


class FusionInput(BaseModel):
    mission_id: int

    telemetry: dict[str, Any] | None = None
    thermal: dict[str, Any] | None = None
    wavelet: dict[str, Any] | None = None
    orbital: dict[str, Any] | None = None
    space_weather: dict[str, Any] | None = None


@router.post("/")
def analyze_fusion(
    request: FusionInput,
    db: Session = Depends(get_db),
):
    result = fusion.fuse(
        telemetry=request.telemetry,
        thermal=request.thermal,
        wavelet=request.wavelet,
        orbital=request.orbital,
        space_weather=request.space_weather,
    )

    # Store the fusion result.

    event = FusionEvent(
        mission_id=request.mission_id,
        anomaly_count=result["anomaly_count"],
        multi_modal_agreement=result["multi_modal_agreement"],
        anomalous_modalities=",".join(
            result["anomalous_modalities"]
        ),
    )

    db.add(event)
    db.commit()

    return {
        "mission_id": request.mission_id,
        "available_modalities":
            result["available_modalities"],
        "anomalous_modalities":
            result["anomalous_modalities"],
        "normal_modalities":
            result["normal_modalities"],
        "anomaly_count":
            result["anomaly_count"],
        "multi_modal_agreement":
            result["multi_modal_agreement"],
        "stored_in_database": True,
    }
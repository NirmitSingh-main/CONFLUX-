from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import (
    Mission,
    Observation,
    AnomalyEvent,
    FusionEvent,
)


router = APIRouter()


# --------------------------------------------------
# Request model
# --------------------------------------------------

class MissionCreate(BaseModel):
    mission_name: str
    spacecraft_name: str
    status: str = "ACTIVE"


# --------------------------------------------------
# Create mission
# --------------------------------------------------

@router.post("/")
def create_mission(
    mission: MissionCreate,
    db: Session = Depends(get_db),
):
    new_mission = Mission(
        mission_name=mission.mission_name,
        spacecraft_name=mission.spacecraft_name,
        status=mission.status,
    )

    db.add(new_mission)
    db.commit()
    db.refresh(new_mission)

    return {
        "id": new_mission.id,
        "mission_name": new_mission.mission_name,
        "spacecraft_name": new_mission.spacecraft_name,
        "status": new_mission.status,
        "created_at": new_mission.created_at,
    }


# --------------------------------------------------
# Get all missions
# --------------------------------------------------

@router.get("/")
def get_missions(
    db: Session = Depends(get_db),
):
    missions = db.query(Mission).all()

    return [
        {
            "id": mission.id,
            "mission_name": mission.mission_name,
            "spacecraft_name": mission.spacecraft_name,
            "status": mission.status,
            "created_at": mission.created_at,
        }
        for mission in missions
    ]


# --------------------------------------------------
# Get one mission
# --------------------------------------------------

@router.get("/{mission_id}")
def get_mission(
    mission_id: int,
    db: Session = Depends(get_db),
):
    mission = (
        db.query(Mission)
        .filter(Mission.id == mission_id)
        .first()
    )

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found.",
        )

    return {
        "id": mission.id,
        "mission_name": mission.mission_name,
        "spacecraft_name": mission.spacecraft_name,
        "status": mission.status,
        "created_at": mission.created_at,
    }


# --------------------------------------------------
# Get observations for a mission
# --------------------------------------------------

@router.get("/{mission_id}/observations")
def get_mission_observations(
    mission_id: int,
    db: Session = Depends(get_db),
):
    observations = (
        db.query(Observation)
        .filter(Observation.mission_id == mission_id)
        .order_by(Observation.created_at.desc())
        .all()
    )

    return [
        {
            "id": obs.id,
            "mission_id": obs.mission_id,
            "modality": obs.modality,
            "value": obs.value,
            "event": obs.event,
            "created_at": obs.created_at,
        }
        for obs in observations
    ]


# --------------------------------------------------
# Get anomaly events for a mission
# --------------------------------------------------

@router.get("/{mission_id}/anomalies")
def get_mission_anomalies(
    mission_id: int,
    db: Session = Depends(get_db),
):
    anomalies = (
        db.query(AnomalyEvent)
        .filter(AnomalyEvent.mission_id == mission_id)
        .order_by(AnomalyEvent.created_at.desc())
        .all()
    )

    return [
        {
            "id": a.id,
            "mission_id": a.mission_id,
            "modality": a.modality,
            "anomaly_type": a.anomaly_type,
            "description": a.description,
            "created_at": a.created_at,
        }
        for a in anomalies
    ]


# --------------------------------------------------
# Get fusion events for a mission
# --------------------------------------------------

@router.get("/{mission_id}/fusion")
def get_mission_fusion_events(
    mission_id: int,
    db: Session = Depends(get_db),
):
    fusion_events = (
        db.query(FusionEvent)
        .filter(FusionEvent.mission_id == mission_id)
        .order_by(FusionEvent.created_at.desc())
        .all()
    )

    return [
        {
            "id": fe.id,
            "mission_id": fe.mission_id,
            "anomaly_count": fe.anomaly_count,
            "multi_modal_agreement": fe.multi_modal_agreement,
            "anomalous_modalities": fe.anomalous_modalities.split(",") if fe.anomalous_modalities else [],
            "created_at": fe.created_at,
        }
        for fe in fusion_events
    ]
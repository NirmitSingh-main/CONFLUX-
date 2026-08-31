from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import Mission


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
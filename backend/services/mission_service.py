from sqlalchemy.orm import Session
from backend.database.models import Mission, Observation, AnomalyEvent, FusionEvent


class MissionService:
    """
    Service responsible for managing spacecraft mission lifecycle,
    querying observations, anomalies, and active mission states.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_mission(
        self,
        mission_name: str,
        spacecraft_name: str,
        status: str = "ACTIVE",
    ) -> Mission:
        new_mission = Mission(
            mission_name=mission_name,
            spacecraft_name=spacecraft_name,
            status=status,
        )
        self.db.add(new_mission)
        self.db.commit()
        self.db.refresh(new_mission)
        return new_mission

    def get_missions(self) -> list[Mission]:
        return self.db.query(Mission).order_by(Mission.id.desc()).all()

    def get_mission_by_id(self, mission_id: int) -> Mission | None:
        return self.db.query(Mission).filter(Mission.id == mission_id).first()

    def update_mission_status(self, mission_id: int, status: str) -> Mission | None:
        mission = self.get_mission_by_id(mission_id)
        if mission:
            mission.status = status
            self.db.commit()
            self.db.refresh(mission)
        return mission

    def get_mission_summary(self, mission_id: int) -> dict:
        mission = self.get_mission_by_id(mission_id)
        if not mission:
            return {}

        observations = (
            self.db.query(Observation)
            .filter(Observation.mission_id == mission_id)
            .all()
        )
        anomalies = (
            self.db.query(AnomalyEvent)
            .filter(AnomalyEvent.mission_id == mission_id)
            .all()
        )
        fusion_events = (
            self.db.query(FusionEvent)
            .filter(FusionEvent.mission_id == mission_id)
            .all()
        )

        return {
            "mission": {
                "id": mission.id,
                "mission_name": mission.mission_name,
                "spacecraft_name": mission.spacecraft_name,
                "status": mission.status,
                "created_at": mission.created_at,
            },
            "observation_count": len(observations),
            "anomaly_count": len(anomalies),
            "fusion_event_count": len(fusion_events),
            "recent_anomalies": [
                {
                    "id": a.id,
                    "modality": a.modality,
                    "anomaly_type": a.anomaly_type,
                    "description": a.description,
                    "created_at": a.created_at,
                }
                for a in anomalies[-5:]
            ],
        }

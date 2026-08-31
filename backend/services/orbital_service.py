from datetime import datetime
from backend.models.orbital import OrbitalState, Vector3D
from backend.physics.conjunction import assess_conjunction, ConjunctionResult as ConjunctionAssessment
from backend.intelligence.orbital_risk import OrbitalRiskAnalyzer


class OrbitalService:
    """
    Service responsible for orchestrating orbital mechanics physics
    and risk intelligence for close approach and conjunction evaluations.
    """

    def __init__(self, risk_analyzer: OrbitalRiskAnalyzer | None = None):
        self.risk_analyzer = risk_analyzer or OrbitalRiskAnalyzer()

    def evaluate_conjunction(
        self,
        object1_id: str,
        obj1_timestamp: datetime,
        obj1_pos: Vector3D | dict,
        obj1_vel: Vector3D | dict,
        object2_id: str,
        obj2_timestamp: datetime,
        obj2_pos: Vector3D | dict,
        obj2_vel: Vector3D | dict,
        safety_distance: float = 1.0,
    ) -> dict:
        pos1 = obj1_pos if isinstance(obj1_pos, Vector3D) else Vector3D(**obj1_pos)
        vel1 = obj1_vel if isinstance(obj1_vel, Vector3D) else Vector3D(**obj1_vel)
        pos2 = obj2_pos if isinstance(obj2_pos, Vector3D) else Vector3D(**obj2_pos)
        vel2 = obj2_vel if isinstance(obj2_vel, Vector3D) else Vector3D(**obj2_vel)

        state1 = OrbitalState(
            object_id=object1_id,
            timestamp=obj1_timestamp,
            position=pos1,
            velocity=vel1,
        )

        state2 = OrbitalState(
            object_id=object2_id,
            timestamp=obj2_timestamp,
            position=pos2,
            velocity=vel2,
        )

        conjunction: ConjunctionAssessment = assess_conjunction(
            state1,
            state2,
            safety_distance=safety_distance,
        )

        analysis = self.risk_analyzer.analyze(conjunction)

        return {
            "object1_id": analysis["object1_id"],
            "object2_id": analysis["object2_id"],
            "current_distance": analysis["current_distance"],
            "relative_speed": conjunction.relative_speed,
            "time_to_closest_approach": analysis["time_to_closest_approach"],
            "miss_distance": analysis["miss_distance"],
            "collision_risk": analysis["collision_risk"],
            "status": analysis["status"],
            "event_type": analysis["event_type"],
            "risk_level": conjunction.risk_level,
        }

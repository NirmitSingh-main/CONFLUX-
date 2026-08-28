from backend.physics.conjunction import ConjunctionResult


class OrbitalRiskAnalyzer:
    """
    Analyze orbital conjunction results.

    This module interprets physical measurements calculated
    by the conjunction physics module. It does not calculate
    an artificial probability of collision.
    """

    def __init__(
        self,
        warning_distance: float = 10.0,
        critical_distance: float = 1.0,
    ):
        if warning_distance <= 0:
            raise ValueError(
                "Warning distance must be greater than zero."
            )

        if critical_distance <= 0:
            raise ValueError(
                "Critical distance must be greater than zero."
            )

        if critical_distance >= warning_distance:
            raise ValueError(
                "Critical distance must be smaller than "
                "warning distance."
            )

        self.warning_distance = warning_distance
        self.critical_distance = critical_distance

    def analyze(
        self,
        conjunction: ConjunctionResult,
    ) -> dict:
        """
        Interpret a conjunction result.

        Distances are measured in kilometers.
        Time is measured in seconds.
        """

        miss_distance = conjunction.miss_distance

        if conjunction.collision_risk:
            status = "CRITICAL"
            event_type = "SAFETY_DISTANCE_VIOLATION"

        elif miss_distance <= self.critical_distance:
            status = "CRITICAL"
            event_type = "CRITICAL_CLOSE_APPROACH"

        elif miss_distance <= self.warning_distance:
            status = "WARNING"
            event_type = "CLOSE_APPROACH"

        else:
            status = "NOMINAL"
            event_type = "NO_SIGNIFICANT_CONJUNCTION"

        return {
            "object1_id": conjunction.object1_id,
            "object2_id": conjunction.object2_id,
            "current_distance": conjunction.current_distance,
            "time_to_closest_approach": (
                conjunction.time_to_closest_approach
            ),
            "miss_distance": conjunction.miss_distance,
            "collision_risk": conjunction.collision_risk,
            "status": status,
            "event_type": event_type,
            "warning_distance": self.warning_distance,
            "critical_distance": self.critical_distance,
        }
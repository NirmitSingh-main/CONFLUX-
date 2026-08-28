from dataclasses import dataclass

import numpy as np

from backend.models.orbital import OrbitalState
from backend.physics.relative_motion import (
    calculate_relative_position,
    calculate_relative_velocity,
    calculate_time_to_closest_approach,
)


@dataclass
class ConjunctionResult:
    object1_id: str
    object2_id: str

    current_distance: float
    relative_speed: float

    time_to_closest_approach: float
    miss_distance: float

    collision_risk: bool
    risk_level: str


def assess_conjunction(
    state1: OrbitalState,
    state2: OrbitalState,
    safety_distance: float = 1.0,
) -> ConjunctionResult:
    """
    Assess the potential conjunction between two orbital objects.

    Distances are measured in kilometers.
    Velocity is measured in kilometers per second.
    Time is measured in seconds.

    This is a simplified constant-relative-velocity model.
    It is intended for CONFLUX's prototype risk-analysis layer.
    """

    if safety_distance <= 0:
        raise ValueError("Safety distance must be greater than zero.")

    relative_position = calculate_relative_position(
        state1,
        state2,
    )

    relative_velocity = calculate_relative_velocity(
        state1,
        state2,
    )

    current_distance = float(
        np.linalg.norm(relative_position)
    )

    relative_speed = float(
        np.linalg.norm(relative_velocity)
    )

    time_to_ca = calculate_time_to_closest_approach(
        state1,
        state2,
    )

    # If closest approach has already occurred,
    # treat the current state as the closest point.
    if time_to_ca < 0:
        time_to_ca = 0.0

    closest_position = (
        relative_position
        + relative_velocity * time_to_ca
    )

    miss_distance = float(
        np.linalg.norm(closest_position)
    )

    collision_risk = miss_distance <= safety_distance

    # Prototype risk classification.
    if miss_distance <= safety_distance:
        risk_level = "CRITICAL"
    elif miss_distance <= safety_distance * 5:
        risk_level = "HIGH"
    elif miss_distance <= safety_distance * 10:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return ConjunctionResult(
        object1_id=state1.object_id,
        object2_id=state2.object_id,
        current_distance=current_distance,
        relative_speed=relative_speed,
        time_to_closest_approach=time_to_ca,
        miss_distance=miss_distance,
        collision_risk=collision_risk,
        risk_level=risk_level,
    )
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
    time_to_closest_approach: float
    miss_distance: float
    collision_risk: bool


def assess_conjunction(
    state1: OrbitalState,
    state2: OrbitalState,
    safety_distance: float = 1.0,
) -> ConjunctionResult:
    """
    Assess a potential conjunction between two objects.

    Distances are measured in kilometers.
    Time is measured in seconds.
    """

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

    time_to_ca = calculate_time_to_closest_approach(
        state1,
        state2,
    )

    # If closest approach is in the past,
    # the current state is the closest point
    # under the constant-relative-velocity assumption.
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

    return ConjunctionResult(
        object1_id=state1.object_id,
        object2_id=state2.object_id,
        current_distance=current_distance,
        time_to_closest_approach=time_to_ca,
        miss_distance=miss_distance,
        collision_risk=collision_risk,
    )
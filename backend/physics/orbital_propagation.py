import numpy as np

from backend.models.orbital import OrbitalState
from backend.physics.constants import EARTH_MU


def calculate_acceleration(position: np.ndarray) -> np.ndarray:
    """
    Calculate Earth's gravitational acceleration
    for a position given in kilometers.
    """

    distance = np.linalg.norm(position)

    if distance == 0:
        raise ValueError("Position cannot be at Earth's center.")

    acceleration = -EARTH_MU * position / distance**3

    return acceleration


def propagate_orbit(
    state: OrbitalState,
    duration: float,
    time_step: float = 10.0,
) -> OrbitalState:
    """
    Propagate an orbital state forward in time.

    Parameters:
        state: Current orbital state.
        duration: Propagation time in seconds.
        time_step: Simulation step in seconds.

    Returns:
        Estimated orbital state after the requested duration.
    """

    position = np.array(
        [
            state.position.x,
            state.position.y,
            state.position.z,
        ],
        dtype=float,
    )

    velocity = np.array(
        [
            state.velocity.x,
            state.velocity.y,
            state.velocity.z,
        ],
        dtype=float,
    )

    elapsed = 0.0

    while elapsed < duration:
        step = min(time_step, duration - elapsed)

        acceleration = calculate_acceleration(position)

        velocity = velocity + acceleration * step
        position = position + velocity * step

        elapsed += step

    return OrbitalState(
        object_id=state.object_id,
        timestamp=state.timestamp,
        position={
            "x": position[0],
            "y": position[1],
            "z": position[2],
        },
        velocity={
            "x": velocity[0],
            "y": velocity[1],
            "z": velocity[2],
        },
    )
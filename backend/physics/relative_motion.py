import numpy as np

from backend.models.orbital import OrbitalState


def _position_vector(state: OrbitalState) -> np.ndarray:
    """Convert an orbital position into a NumPy vector."""

    return np.array(
        [
            state.position.x,
            state.position.y,
            state.position.z,
        ],
        dtype=float,
    )


def _velocity_vector(state: OrbitalState) -> np.ndarray:
    """Convert an orbital velocity into a NumPy vector."""

    return np.array(
        [
            state.velocity.x,
            state.velocity.y,
            state.velocity.z,
        ],
        dtype=float,
    )


def calculate_relative_position(
    state1: OrbitalState,
    state2: OrbitalState,
) -> np.ndarray:
    """
    Calculate the position of object 2 relative to object 1.

    Returns:
        Relative position vector in kilometers.
    """

    return _position_vector(state2) - _position_vector(state1)


def calculate_relative_velocity(
    state1: OrbitalState,
    state2: OrbitalState,
) -> np.ndarray:
    """
    Calculate the velocity of object 2 relative to object 1.

    Returns:
        Relative velocity vector in kilometers per second.
    """

    return _velocity_vector(state2) - _velocity_vector(state1)


def calculate_distance(
    state1: OrbitalState,
    state2: OrbitalState,
) -> float:
    """
    Calculate the distance between two orbital objects.

    Returns:
        Distance in kilometers.
    """

    relative_position = calculate_relative_position(
        state1,
        state2,
    )

    return float(np.linalg.norm(relative_position))


def calculate_time_to_closest_approach(
    state1: OrbitalState,
    state2: OrbitalState,
) -> float:
    """
    Estimate time to closest approach assuming
    constant relative velocity.

    Returns:
        Time to closest approach in seconds.

        Positive value  -> closest approach is in the future.
        Negative value  -> closest approach was in the past.
        Zero             -> objects are currently at closest approach.
    """

    relative_position = calculate_relative_position(
        state1,
        state2,
    )

    relative_velocity = calculate_relative_velocity(
        state1,
        state2,
    )

    velocity_squared = float(
        np.dot(relative_velocity, relative_velocity)
    )

    # Objects have no relative motion.
    if np.isclose(velocity_squared, 0.0):
        return 0.0

    time_to_ca = -float(
        np.dot(relative_position, relative_velocity)
    ) / velocity_squared

    return time_to_ca
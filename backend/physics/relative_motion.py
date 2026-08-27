import numpy as np

from backend.models.orbital import OrbitalState


def calculate_relative_position(
    state1: OrbitalState,
    state2: OrbitalState,
) -> np.ndarray:
    """Calculate relative position of object 2 with respect to object 1."""

    position1 = np.array([
        state1.position.x,
        state1.position.y,
        state1.position.z,
    ], dtype=float)

    position2 = np.array([
        state2.position.x,
        state2.position.y,
        state2.position.z,
    ], dtype=float)

    return position2 - position1


def calculate_relative_velocity(
    state1: OrbitalState,
    state2: OrbitalState,
) -> np.ndarray:
    """Calculate relative velocity of object 2 with respect to object 1."""

    velocity1 = np.array([
        state1.velocity.x,
        state1.velocity.y,
        state1.velocity.z,
    ], dtype=float)

    velocity2 = np.array([
        state2.velocity.x,
        state2.velocity.y,
        state2.velocity.z,
    ], dtype=float)

    return velocity2 - velocity1


def calculate_distance(
    state1: OrbitalState,
    state2: OrbitalState,
) -> float:
    """Calculate distance between two objects."""

    relative_position = calculate_relative_position(state1, state2)

    return float(np.linalg.norm(relative_position))


def calculate_time_to_closest_approach(
    state1: OrbitalState,
    state2: OrbitalState,
) -> float:
    """
    Estimate time until closest approach assuming
    constant relative velocity.
    """

    relative_position = calculate_relative_position(state1, state2)
    relative_velocity = calculate_relative_velocity(state1, state2)

    velocity_squared = np.dot(relative_velocity, relative_velocity)

    if velocity_squared == 0:
        return 0.0

    time_to_ca = -np.dot(
        relative_position,
        relative_velocity,
    ) / velocity_squared

    return float(time_to_ca)
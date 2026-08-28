import numpy as np

from backend.models.orbital import OrbitalState, Vector3D
from backend.physics.constants import EARTH_MU


def calculate_acceleration(position: np.ndarray) -> np.ndarray:
    """
    Calculate Earth's gravitational acceleration.

    Parameters:
        position: Position vector in kilometers.

    Returns:
        Acceleration vector in kilometers per second squared.
    """

    position = np.asarray(position, dtype=float)

    if position.shape != (3,):
        raise ValueError("Position must contain exactly 3 components.")

    distance = np.linalg.norm(position)

    if distance <= 0:
        raise ValueError("Position cannot be at Earth's center.")

    return -EARTH_MU * position / distance**3


def _derivatives(
    position: np.ndarray,
    velocity: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return position and velocity derivatives for orbital motion.
    """

    acceleration = calculate_acceleration(position)

    return velocity, acceleration


def propagate_orbit(
    state: OrbitalState,
    duration: float,
    time_step: float = 10.0,
) -> OrbitalState:
    """
    Propagate an orbital state forward in time using RK4.

    Parameters:
        state: Current orbital state.
        duration: Propagation time in seconds.
        time_step: Integration step in seconds.

    Returns:
        Estimated orbital state after the requested duration.

    Units:
        Position: km
        Velocity: km/s
        Time: seconds
    """

    if duration < 0:
        raise ValueError("Duration cannot be negative.")

    if time_step <= 0:
        raise ValueError("Time step must be greater than zero.")

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

        # RK4 - Step 1
        k1_position, k1_velocity = _derivatives(
            position,
            velocity,
        )

        # RK4 - Step 2
        k2_position, k2_velocity = _derivatives(
            position + 0.5 * step * k1_position,
            velocity + 0.5 * step * k1_velocity,
        )

        # RK4 - Step 3
        k3_position, k3_velocity = _derivatives(
            position + 0.5 * step * k2_position,
            velocity + 0.5 * step * k2_velocity,
        )

        # RK4 - Step 4
        k4_position, k4_velocity = _derivatives(
            position + step * k3_position,
            velocity + step * k3_velocity,
        )

        # Combine RK4 estimates.
        position += (
            step
            / 6.0
            * (
                k1_position
                + 2.0 * k2_position
                + 2.0 * k3_position
                + k4_position
            )
        )

        velocity += (
            step
            / 6.0
            * (
                k1_velocity
                + 2.0 * k2_velocity
                + 2.0 * k3_velocity
                + k4_velocity
            )
        )

        elapsed += step

    # Update the timestamp because the state has been propagated.
    new_timestamp = state.timestamp + __import__("datetime").timedelta(
        seconds=duration
    )

    return OrbitalState(
        object_id=state.object_id,
        timestamp=new_timestamp,
        position=Vector3D(
            x=float(position[0]),
            y=float(position[1]),
            z=float(position[2]),
        ),
        velocity=Vector3D(
            x=float(velocity[0]),
            y=float(velocity[1]),
            z=float(velocity[2]),
        ),
    )
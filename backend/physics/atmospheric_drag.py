import numpy as np


def calculate_drag_acceleration(
    velocity: np.ndarray,
    density: float,
    drag_coefficient: float,
    area: float,
    mass: float,
) -> np.ndarray:
    """
    Calculate atmospheric drag acceleration.

    Parameters:
        velocity: Object velocity relative to the atmosphere (km/s)
        density: Atmospheric density (kg/m^3)
        drag_coefficient: Dimensionless drag coefficient
        area: Cross-sectional area (m^2)
        mass: Spacecraft mass (kg)

    Returns:
        Drag acceleration vector in km/s^2.
    """

    velocity = np.asarray(velocity, dtype=float)

    if velocity.shape != (3,):
        raise ValueError("Velocity must contain exactly 3 components.")

    if density < 0:
        raise ValueError("Atmospheric density cannot be negative.")

    if drag_coefficient < 0:
        raise ValueError("Drag coefficient cannot be negative.")

    if area < 0:
        raise ValueError("Cross-sectional area cannot be negative.")

    if mass <= 0:
        raise ValueError("Spacecraft mass must be greater than zero.")

    # Convert velocity from km/s to m/s.
    velocity_ms = velocity * 1000.0

    speed_ms = np.linalg.norm(velocity_ms)

    # No relative motion means no atmospheric drag.
    if speed_ms == 0:
        return np.zeros(3, dtype=float)

    # Unit vector in the direction of motion.
    direction = velocity_ms / speed_ms

    # Drag acceleration:
    #
    # a = -1/2 * Cd * (A/m) * rho * v^2
    #
    # Direction is opposite to the velocity vector.
    acceleration_ms2 = (
        -0.5
        * drag_coefficient
        * (area / mass)
        * density
        * speed_ms**2
        * direction
    )

    # Convert m/s^2 to km/s^2.
    acceleration_kms2 = acceleration_ms2 / 1000.0

    return acceleration_kms2
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

    speed = np.linalg.norm(velocity)

    if speed == 0:
        return np.zeros(3)

    # Convert velocity from km/s to m/s
    velocity_ms = velocity * 1000.0

    speed_ms = np.linalg.norm(velocity_ms)

    direction = velocity_ms / speed_ms

    acceleration_ms2 = (
        -0.5
        * drag_coefficient
        * area
        / mass
        * density
        * speed_ms**2
        * direction
    )

    # Convert m/s² to km/s²
    acceleration_kms2 = acceleration_ms2 / 1000.0

    return acceleration_kms2
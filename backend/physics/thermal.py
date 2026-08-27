import math


# Stefan-Boltzmann constant
STEFAN_BOLTZMANN = 5.670374419e-8  # W / m^2 / K^4


def celsius_to_kelvin(temperature_celsius: float) -> float:
    """Convert temperature from Celsius to Kelvin."""

    return temperature_celsius + 273.15


def calculate_thermal_power(
    temperature_celsius: float,
    area: float,
    emissivity: float = 1.0,
) -> float:
    """
    Calculate thermal radiation power using
    the Stefan-Boltzmann law.

    Returns power in watts.
    """

    if area < 0:
        raise ValueError("Area cannot be negative.")

    if not 0 <= emissivity <= 1:
        raise ValueError("Emissivity must be between 0 and 1.")

    temperature_kelvin = celsius_to_kelvin(
        temperature_celsius
    )

    power = (
        emissivity
        * STEFAN_BOLTZMANN
        * area
        * temperature_kelvin**4
    )

    return power
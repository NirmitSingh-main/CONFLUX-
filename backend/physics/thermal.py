from backend.physics.constants import STEFAN_BOLTZMANN


def celsius_to_kelvin(temperature_celsius: float) -> float:
    """
    Convert temperature from Celsius to Kelvin.
    """

    temperature_kelvin = temperature_celsius + 273.15

    if temperature_kelvin < 0:
        raise ValueError(
            "Temperature cannot be below absolute zero."
        )

    return temperature_kelvin


def calculate_thermal_power(
    temperature_celsius: float,
    area: float,
    emissivity: float = 1.0,
) -> float:
    """
    Calculate emitted thermal radiation power
    using the Stefan-Boltzmann law.

    Formula:
        P = εσAT^4

    Parameters:
        temperature_celsius: Surface temperature in Celsius.
        area: Radiating surface area in square meters.
        emissivity: Surface emissivity between 0 and 1.

    Returns:
        Thermal radiation power in watts.
    """

    if area < 0:
        raise ValueError("Area cannot be negative.")

    if not 0 <= emissivity <= 1:
        raise ValueError(
            "Emissivity must be between 0 and 1."
        )

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
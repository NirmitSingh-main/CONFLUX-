def calculate_radiation_exposure(
    particle_flux: float,
    particle_energy: float,
    exposure_time: float,
) -> float:
    """
    Calculate a simplified radiation exposure indicator.

    Parameters:
        particle_flux: Particle flux.
        particle_energy: Representative particle energy.
        exposure_time: Exposure duration in seconds.

    Returns:
        Simplified radiation exposure score.
    """

    if particle_flux < 0:
        raise ValueError("Particle flux cannot be negative.")

    if particle_energy < 0:
        raise ValueError("Particle energy cannot be negative.")

    if exposure_time < 0:
        raise ValueError("Exposure time cannot be negative.")

    exposure = (
        particle_flux
        * particle_energy
        * exposure_time
    )

    return exposure
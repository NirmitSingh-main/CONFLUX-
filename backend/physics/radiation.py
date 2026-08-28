def calculate_radiation_exposure_index(
    particle_flux: float,
    particle_energy: float,
    exposure_time: float,
) -> float:
    """
    Calculate a simplified radiation exposure index.

    This is an environmental indicator for CONFLUX.
    It is NOT a physical absorbed-dose calculation.

    Parameters:
        particle_flux: Particle flux.
        particle_energy: Representative particle energy.
        exposure_time: Exposure duration in seconds.

    Returns:
        Radiation exposure index.
    """

    if particle_flux < 0:
        raise ValueError("Particle flux cannot be negative.")

    if particle_energy < 0:
        raise ValueError("Particle energy cannot be negative.")

    if exposure_time < 0:
        raise ValueError("Exposure time cannot be negative.")

    return particle_flux * particle_energy * exposure_time
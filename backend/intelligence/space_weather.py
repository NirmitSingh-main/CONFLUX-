class SpaceWeatherAnalyzer:
    """
    Analyze spacecraft-relevant space-weather observations.

    The analyzer works with measured values and configurable
    thresholds. It does not convert measurements into an
    artificial probability or risk score.
    """

    def __init__(
        self,
        solar_activity_threshold: float | None = None,
        radiation_threshold: float | None = None,
        geomagnetic_activity_threshold: float | None = None,
    ):
        self.solar_activity_threshold = (
            solar_activity_threshold
        )

        self.radiation_threshold = radiation_threshold

        self.geomagnetic_activity_threshold = (
            geomagnetic_activity_threshold
        )

    def _validate(
        self,
        value: float,
        name: str,
    ) -> None:
        """Validate a physical measurement."""

        if value < 0:
            raise ValueError(
                f"{name} cannot be negative."
            )

    def _check_threshold(
        self,
        value: float,
        threshold: float | None,
    ) -> bool:
        """Check whether a configured threshold is exceeded."""

        if threshold is None:
            return False

        return value >= threshold

    def analyze(
        self,
        solar_activity: float,
        radiation_level: float,
        geomagnetic_activity: float,
    ) -> dict:
        """
        Analyze space-weather measurements.

        The units depend on the selected data source.
        """

        self._validate(
            solar_activity,
            "Solar activity",
        )

        self._validate(
            radiation_level,
            "Radiation level",
        )

        self._validate(
            geomagnetic_activity,
            "Geomagnetic activity",
        )

        solar_event = self._check_threshold(
            solar_activity,
            self.solar_activity_threshold,
        )

        radiation_event = self._check_threshold(
            radiation_level,
            self.radiation_threshold,
        )

        geomagnetic_event = self._check_threshold(
            geomagnetic_activity,
            self.geomagnetic_activity_threshold,
        )

        active_events = []

        if solar_event:
            active_events.append(
                "ELEVATED_SOLAR_ACTIVITY"
            )

        if radiation_event:
            active_events.append(
                "ELEVATED_RADIATION"
            )

        if geomagnetic_event:
            active_events.append(
                "ELEVATED_GEOMAGNETIC_ACTIVITY"
            )

        return {
            "solar_activity": solar_activity,
            "radiation_level": radiation_level,
            "geomagnetic_activity": geomagnetic_activity,
            "solar_event": solar_event,
            "radiation_event": radiation_event,
            "geomagnetic_event": geomagnetic_event,
            "active_events": active_events,
            "environmental_anomaly": bool(
                active_events
            ),
        }
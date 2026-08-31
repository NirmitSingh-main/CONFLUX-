from backend.intelligence.space_weather import SpaceWeatherAnalyzer


class SpaceWeatherService:
    """
    Service responsible for space-weather environmental monitoring,
    solar flux analysis, radiation surge tracking, and geomagnetic storm detection.
    """

    def __init__(
        self,
        solar_activity_threshold: float = 492.545,
        radiation_threshold: float = 7.749,
        geomagnetic_activity_threshold: float = 3.565,
    ):
        self.analyzer = SpaceWeatherAnalyzer(
            solar_activity_threshold=solar_activity_threshold,
            radiation_threshold=radiation_threshold,
            geomagnetic_activity_threshold=geomagnetic_activity_threshold,
        )

    def analyze_conditions(
        self,
        solar_activity: float,
        radiation_level: float,
        geomagnetic_activity: float,
    ) -> dict:
        return self.analyzer.analyze(
            solar_activity=solar_activity,
            radiation_level=radiation_level,
            geomagnetic_activity=geomagnetic_activity,
        )

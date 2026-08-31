from typing import Any
from backend.services.telemetry_service import TelemetryService
from backend.services.orbital_service import OrbitalService
from backend.services.weather_service import SpaceWeatherService
from backend.services.imagery_service import ImageryService
from backend.services.fusion_service import FusionService


class IntelligenceService:
    """
    Unified Orchestrator Service providing a single facade for all
    CONFLUX intelligent analysis pipelines and physics engines.
    """

    def __init__(self):
        self.telemetry_service = TelemetryService()
        self.orbital_service = OrbitalService()
        self.weather_service = SpaceWeatherService()
        self.imagery_service = ImageryService()
        self.fusion_service = FusionService()

    def run_full_pipeline_synthesis(
        self,
        telemetry_result: dict[str, Any] | None = None,
        thermal_result: dict[str, Any] | None = None,
        wavelet_result: dict[str, Any] | None = None,
        orbital_result: dict[str, Any] | None = None,
        weather_result: dict[str, Any] | None = None,
    ) -> dict:
        return self.fusion_service.fuse_modalities(
            telemetry=telemetry_result,
            thermal=thermal_result,
            wavelet=wavelet_result,
            orbital=orbital_result,
            space_weather=weather_result,
        )

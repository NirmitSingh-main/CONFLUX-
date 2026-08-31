from typing import Any
from backend.intelligence.multimodal_fusion import MultimodalFusion


class FusionService:
    """
    Service responsible for multimodal cross-subsystem consensus evaluation
    across telemetry, thermal, wavelet, orbital, and space weather modalities.
    """

    def __init__(self, fusion_engine: MultimodalFusion | None = None):
        self.fusion = fusion_engine or MultimodalFusion()

    def fuse_modalities(
        self,
        telemetry: dict[str, Any] | None = None,
        thermal: dict[str, Any] | None = None,
        wavelet: dict[str, Any] | None = None,
        orbital: dict[str, Any] | None = None,
        space_weather: dict[str, Any] | None = None,
    ) -> dict:
        return self.fusion.fuse(
            telemetry=telemetry,
            thermal=thermal,
            wavelet=wavelet,
            orbital=orbital,
            space_weather=space_weather,
        )

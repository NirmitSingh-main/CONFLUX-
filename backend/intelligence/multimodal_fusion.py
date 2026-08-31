from typing import Any


class MultimodalFusion:
    """
    Combine observations from CONFLUX intelligence modules.

    Each modality remains individually identifiable.
    The fusion layer detects agreement between independent
    observations.

    No artificial risk or confidence score is generated.
    """

    def _contains_anomaly(
        self,
        result: dict[str, Any],
    ) -> bool:
        """
        Determine whether a module reports an abnormal event.
        """

        # Telemetry / Wavefront / Thermal
        if result.get("anomaly_detected") is True:
            return True

        # Space Weather
        if result.get("environmental_anomaly") is True:
            return True

        # Orbital
        if result.get("collision_risk") is True:
            return True

        # Modules using explicit status values
        if result.get("status") in {
            "WARNING",
            "CRITICAL",
            "ANOMALOUS",
        }:
            return True

        # Existing explicit risk-level output
        if result.get("risk_level") in {
            "HIGH",
            "CRITICAL",
        }:
            return True

        return False

    def fuse(
        self,
        telemetry: dict[str, Any] | None = None,
        thermal: dict[str, Any] | None = None,
        wavelet: dict[str, Any] | None = None,
        orbital: dict[str, Any] | None = None,
        space_weather: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Combine available modality observations.

        No modality is discarded or converted into an
        artificial numerical risk score.
        """

        observations = {
            "telemetry": telemetry,
            "thermal": thermal,
            "wavelet": wavelet,
            "orbital": orbital,
            "space_weather": space_weather,
        }

        available_observations = {
            name: result
            for name, result in observations.items()
            if result is not None
        }

        anomalous_modalities = [
            name
            for name, result in available_observations.items()
            if self._contains_anomaly(result)
        ]

        normal_modalities = [
            name
            for name, result in available_observations.items()
            if not self._contains_anomaly(result)
        ]

        anomaly_count = len(
            anomalous_modalities
        )

        return {
            "observations": available_observations,

            "available_modalities": list(
                available_observations.keys()
            ),

            "anomalous_modalities":
                anomalous_modalities,

            "normal_modalities":
                normal_modalities,

            "anomaly_count":
                anomaly_count,

            "multi_modal_agreement": (
                anomaly_count >= 2
            ),
        }
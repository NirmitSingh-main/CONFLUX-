from typing import Any


class MultimodalFusion:
    """
    Combine observations from CONFLUX intelligence modules.

    The fusion layer preserves evidence from each modality
    and identifies agreement between independent observations.

    It does not generate arbitrary risk or confidence scores.
    """

    def __init__(
        self,
        anomaly_threshold: float = 0.5,
    ):
        if not 0 <= anomaly_threshold <= 1:
            raise ValueError(
                "Anomaly threshold must be between 0 and 1."
            )

        self.anomaly_threshold = anomaly_threshold

    def _contains_anomaly(
        self,
        result: dict[str, Any],
    ) -> bool:
        """
        Determine whether a module reports an abnormal event.
        """

        if result.get("anomaly_detected") is True:
            return True

        if result.get("environmental_anomaly") is True:
            return True

        if result.get("collision_risk") is True:
            return True

        if result.get("status") in {
            "WARNING",
            "CRITICAL",
            "ANOMALOUS",
        }:
            return True

        if result.get("risk_level") in {
            "HIGH",
            "CRITICAL",
        }:
            return True

        score = result.get("anomaly_score")

        if isinstance(score, (int, float)):
            return score >= self.anomaly_threshold

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

        Each modality remains individually identifiable so
        downstream mission logic can determine what happened.
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

        return {
            "observations": available_observations,
            "available_modalities": list(
                available_observations.keys()
            ),
            "anomalous_modalities": anomalous_modalities,
            "normal_modalities": normal_modalities,
            "anomaly_count": len(
                anomalous_modalities
            ),
            "multi_modal_agreement": (
                len(anomalous_modalities) >= 2
            ),
        }
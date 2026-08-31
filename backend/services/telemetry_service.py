import numpy as np

from backend.intelligence.telemetry_anomaly import (
    TelemetryAnomalyDetector,
)
from backend.models.telemetry import TelemetryReading


class TelemetryService:
    """
    Service responsible for processing spacecraft telemetry.
    """

    FEATURES = [
        "temperature",
        "voltage",
        "current",
        "battery",
        "pressure",
        "vibration",
    ]

    def __init__(
        self,
        detector: TelemetryAnomalyDetector | None = None,
    ):
        self.detector = (
            detector
            or TelemetryAnomalyDetector()
        )

    def _to_array(
        self,
        readings: list[TelemetryReading],
    ) -> np.ndarray:
        """
        Convert telemetry readings into the feature matrix
        expected by the anomaly detector.
        """

        if not readings:
            raise ValueError(
                "At least one telemetry reading is required."
            )

        return np.array(
            [
                [
                    reading.temperature,
                    reading.voltage,
                    reading.current,
                    reading.battery,
                    reading.pressure,
                    reading.vibration,
                ]
                for reading in readings
            ],
            dtype=float,
        )

    def train(
        self,
        readings: list[TelemetryReading],
    ) -> None:
        """
        Train the anomaly detector using telemetry readings.
        """

        data = self._to_array(readings)

        self.detector.train(data)

    def analyze(
        self,
        readings: list[TelemetryReading],
    ) -> list[dict]:
        """
        Analyze telemetry readings for anomalies.
        """

        data = self._to_array(readings)

        predictions = self.detector.predict(data)
        scores = self.detector.anomaly_score(data)

        results = []

        for reading, prediction, score in zip(
            readings,
            predictions,
            scores,
        ):
            results.append(
                {
                    "timestamp": reading.timestamp,
                    "anomaly_detected": (
                        int(prediction) == -1
                    ),
                    "anomaly_score": float(score),
                    "telemetry": {
                        "temperature": reading.temperature,
                        "voltage": reading.voltage,
                        "current": reading.current,
                        "battery": reading.battery,
                        "pressure": reading.pressure,
                        "vibration": reading.vibration,
                    },
                }
            )

        return results
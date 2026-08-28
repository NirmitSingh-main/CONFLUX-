import numpy as np
from sklearn.ensemble import IsolationForest


class TelemetryAnomalyDetector:
    """
    Detect unusual spacecraft telemetry using Isolation Forest.

    Input format:
        Each row represents one telemetry observation.

    Example features:
        temperature
        voltage
        current
        battery
        pressure
        vibration
        radiation
        signal_strength
    """

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
    ):
        if not 0 < contamination < 0.5:
            raise ValueError(
                "Contamination must be between 0 and 0.5."
            )

        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
        )

        self.is_trained = False

    def _validate_data(
        self,
        telemetry_data: np.ndarray,
    ) -> np.ndarray:
        """Validate and convert telemetry data."""

        data = np.asarray(
            telemetry_data,
            dtype=float,
        )

        if data.ndim != 2:
            raise ValueError(
                "Telemetry data must be a 2D array."
            )

        if data.shape[0] == 0:
            raise ValueError(
                "Telemetry data cannot be empty."
            )

        if not np.all(np.isfinite(data)):
            raise ValueError(
                "Telemetry data contains invalid values."
            )

        return data

    def train(
        self,
        telemetry_data: np.ndarray,
    ) -> None:
        """
        Train the anomaly detector.

        Each row represents one telemetry observation.
        """

        data = self._validate_data(
            telemetry_data
        )

        self.model.fit(data)
        self.is_trained = True

    def predict(
        self,
        telemetry_data: np.ndarray,
    ) -> np.ndarray:
        """
        Predict whether telemetry observations are normal
        or anomalous.

        Returns:
            1  -> normal
            -1 -> anomaly
        """

        if not self.is_trained:
            raise RuntimeError(
                "Detector must be trained before prediction."
            )

        data = self._validate_data(
            telemetry_data
        )

        return self.model.predict(data)

    def anomaly_score(
        self,
        telemetry_data: np.ndarray,
    ) -> np.ndarray:
        """
        Return normalized anomaly scores.

        Returns:
            Values between 0 and 1.

            Higher value = more anomalous.
        """

        if not self.is_trained:
            raise RuntimeError(
                "Detector must be trained before scoring."
            )

        data = self._validate_data(
            telemetry_data
        )

        raw_scores = self.model.decision_function(
            data
        )

        # Isolation Forest:
        # higher raw score = more normal
        #
        # Convert it so:
        # higher score = more anomalous

        anomaly_scores = 1.0 / (
            1.0 + np.exp(raw_scores)
        )

        return np.clip(
            anomaly_scores,
            0.0,
            1.0,
        )

    def analyze(
        self,
        telemetry_data: np.ndarray,
    ) -> dict:
        """
        Analyze telemetry and return a fusion-ready result.
        """

        predictions = self.predict(
            telemetry_data
        )

        scores = self.anomaly_score(
            telemetry_data
        )

        anomaly_indices = np.where(
            predictions == -1
        )[0]

        return {
            "anomaly_detected": bool(
                len(anomaly_indices) > 0
            ),
            "anomaly_count": int(
                len(anomaly_indices)
            ),
            "anomaly_indices": anomaly_indices.tolist(),
            "max_anomaly_score": float(
                np.max(scores)
            ),
            "mean_anomaly_score": float(
                np.mean(scores)
            ),
        }
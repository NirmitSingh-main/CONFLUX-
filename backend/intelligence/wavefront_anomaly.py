import numpy as np
import pywt


class WavefrontAnomalyDetector:
    """
    Detect anomalies in spacecraft sensor signals using
    Discrete Wavelet Transform (DWT).

    The detector looks for unusual high-frequency energy
    compared with the normal baseline signal.
    """

    def __init__(
        self,
        wavelet: str = "db4",
        level: int = 3,
        threshold: float = 2.5,
    ):
        if level < 1:
            raise ValueError("Wavelet level must be at least 1.")

        if threshold <= 0:
            raise ValueError("Threshold must be greater than zero.")

        self.wavelet = wavelet
        self.level = level
        self.threshold = threshold

        self.baseline_energy: float | None = None

    def _validate_signal(
        self,
        signal: np.ndarray,
    ) -> np.ndarray:
        """Validate and convert the input signal."""

        signal = np.asarray(
            signal,
            dtype=float,
        )

        if signal.ndim != 1:
            raise ValueError(
                "Signal must be a one-dimensional array."
            )

        if len(signal) < 8:
            raise ValueError(
                "Signal must contain at least 8 samples."
            )

        if not np.all(np.isfinite(signal)):
            raise ValueError(
                "Signal contains invalid values."
            )

        return signal

    def _calculate_energy(
        self,
        signal: np.ndarray,
    ) -> float:
        """
        Calculate high-frequency wavelet energy.

        Higher energy can indicate sudden changes,
        vibration, transient events, or other anomalies.
        """

        coefficients = pywt.wavedec(
            signal,
            self.wavelet,
            level=self.level,
        )

        # Ignore approximation coefficients.
        detail_coefficients = coefficients[1:]

        energy = sum(
            np.sum(detail**2)
            for detail in detail_coefficients
        )

        return float(energy)

    def fit(
        self,
        normal_signal: np.ndarray,
    ) -> None:
        """
        Learn the normal wavelet-energy baseline.
        """

        signal = self._validate_signal(
            normal_signal
        )

        self.baseline_energy = self._calculate_energy(
            signal
        )

    def analyze(
        self,
        signal: np.ndarray,
    ) -> dict:
        """
        Analyze a signal for wavelet-based anomalies.
        """

        if self.baseline_energy is None:
            raise RuntimeError(
                "Detector must be fitted before analysis."
            )

        signal = self._validate_signal(
            signal
        )

        energy = self._calculate_energy(
            signal
        )

        # Protect against a zero-energy baseline.
        baseline = max(
            self.baseline_energy,
            1e-12,
        )

        energy_ratio = energy / baseline

        # Convert the ratio into a bounded anomaly score.
        anomaly_score = min(
            energy_ratio / self.threshold,
            1.0,
        )

        anomaly_detected = (
            energy_ratio >= self.threshold
        )

        return {
            "anomaly_detected": anomaly_detected,
            "anomaly_score": float(anomaly_score),
            "wavelet_energy": energy,
            "baseline_energy": self.baseline_energy,
            "energy_ratio": float(energy_ratio),
            "wavelet": self.wavelet,
            "level": self.level,
        }
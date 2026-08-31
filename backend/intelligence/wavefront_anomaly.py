import numpy as np
import pywt


class WavefrontAnomalyDetector:
    """
    Detect abnormal spacecraft wavefront measurements.

    The detector learns normal statistical baselines for the
    wavefront error features and combines them with wavelet
    high-frequency energy.

    Features:
        wavefront_rms_um
        tip_error_um
        tilt_error_um
        defocus_um
        astigmatism_um
        coma_um
    """

    FEATURES = [
        "wavefront_rms_um",
        "tip_error_um",
        "tilt_error_um",
        "defocus_um",
        "astigmatism_um",
        "coma_um",
    ]

    def __init__(
        self,
        wavelet: str = "db4",
        level: int = 2,
        threshold: float = 3.0,
    ):
        if level < 1:
            raise ValueError(
                "Wavelet level must be at least 1."
            )

        if threshold <= 0:
            raise ValueError(
                "Threshold must be greater than zero."
            )

        self.wavelet = wavelet
        self.level = level
        self.threshold = threshold

        self.feature_mean: np.ndarray | None = None
        self.feature_std: np.ndarray | None = None
        self.baseline_energy: float | None = None

    def _validate_features(
        self,
        features: np.ndarray,
    ) -> np.ndarray:
        """Validate feature data."""

        features = np.asarray(
            features,
            dtype=float,
        ).copy()

        if features.ndim != 2:
            raise ValueError(
                "Feature data must be two-dimensional."
            )

        if features.shape[1] != len(self.FEATURES):
            raise ValueError(
                f"Expected {len(self.FEATURES)} features."
            )

        if not np.all(np.isfinite(features)):
            raise ValueError(
                "Feature data contains invalid values."
            )

        return features

    def _validate_signal(
        self,
        signal: np.ndarray,
    ) -> np.ndarray:
        """Validate wavefront signal."""

        signal = np.asarray(
            signal,
            dtype=float,
        ).copy()

        if signal.ndim != 1:
            raise ValueError(
                "Signal must be one-dimensional."
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

    def _calculate_wavelet_energy(
        self,
        signal: np.ndarray,
    ) -> float:
        """Calculate high-frequency wavelet energy."""

        signal = self._validate_signal(signal)

        wavelet = pywt.Wavelet(self.wavelet)

        max_level = pywt.dwt_max_level(
            len(signal),
            wavelet.dec_len,
        )

        level = min(
            self.level,
            max_level,
        )

        if level < 1:
            return 0.0

        coefficients = pywt.wavedec(
            signal,
            wavelet,
            level=level,
        )

        detail_coefficients = coefficients[1:]

        energy = sum(
            np.sum(detail ** 2)
            for detail in detail_coefficients
        )

        return float(energy)

    def fit(
        self,
        normal_features: np.ndarray,
    ) -> None:
        """
        Learn the normal wavefront baseline.

        Training data must contain normal observations only.
        """

        features = self._validate_features(
            normal_features
        )

        if len(features) < 10:
            raise ValueError(
                "At least 10 normal samples are required."
            )

        self.feature_mean = np.mean(
            features,
            axis=0,
        )

        self.feature_std = np.std(
            features,
            axis=0,
        )

        # Prevent division by zero for nearly constant features.
        self.feature_std = np.maximum(
            self.feature_std,
            1e-6,
        )

        # Use RMS wavefront error as the wavelet signal.
        rms_signal = features[:, 0]

        self.baseline_energy = (
            self._calculate_wavelet_energy(
                rms_signal
            )
        )

    def analyze(
        self,
        features: np.ndarray,
        signal: np.ndarray | None = None,
    ) -> dict:
        """
        Analyze wavefront features.

        Parameters:
            features:
                One observation containing all six
                wavefront features.

            signal:
                Optional time-series RMS signal used
                for wavelet analysis.
        """

        if (
            self.feature_mean is None
            or self.feature_std is None
            or self.baseline_energy is None
        ):
            raise RuntimeError(
                "Detector must be fitted before analysis."
            )

        features = np.asarray(
            features,
            dtype=float,
        ).copy()

        if features.ndim != 1:
            raise ValueError(
                "A single observation must be one-dimensional."
            )

        if len(features) != len(self.FEATURES):
            raise ValueError(
                f"Expected {len(self.FEATURES)} features."
            )

        if not np.all(np.isfinite(features)):
            raise ValueError(
                "Features contain invalid values."
            )

        # ---------------------------------------------
        # Statistical deviation from normal baseline.
        # ---------------------------------------------

        signed_z_scores = (
            features
            - self.feature_mean
        ) / self.feature_std
        z_scores = np.abs(signed_z_scores)
        z_scores[0] = max(float(signed_z_scores[0]), 0.0)

        max_z_score = float(
            np.max(z_scores)
        )

        feature_anomaly = (
            max_z_score >= self.threshold
        )

        feature_score = min(
            max_z_score / self.threshold,
            1.0,
        )

        # ---------------------------------------------
        # Optional wavelet analysis.
        # ---------------------------------------------

        wavelet_energy = 0.0
        energy_ratio = 0.0
        wavelet_anomaly = False

        if signal is not None:

            signal = self._validate_signal(
                signal
            )

            wavelet_energy = (
                self._calculate_wavelet_energy(
                    signal
                )
            )

            baseline = max(
                self.baseline_energy,
                1e-12,
            )

            energy_ratio = (
                wavelet_energy / baseline
            )

            wavelet_anomaly = (
                energy_ratio >= self.threshold
            )

        # ---------------------------------------------
        # Final decision.
        # ---------------------------------------------

        anomaly_detected = (
            feature_anomaly
            or wavelet_anomaly
        )

        anomaly_score = max(
            feature_score,
            min(
                energy_ratio / self.threshold,
                1.0,
            ),
        )

        return {
            "anomaly_detected": bool(
                anomaly_detected
            ),
            "anomaly_score": float(
                anomaly_score
            ),
            "max_z_score": max_z_score,
            "feature_scores": {
                name: float(score)
                for name, score in zip(
                    self.FEATURES,
                    z_scores,
                )
            },
            "wavelet_energy": float(
                wavelet_energy
            ),
            "baseline_energy": float(
                self.baseline_energy
            ),
            "energy_ratio": float(
                energy_ratio
            ),
            "wavelet_anomaly": bool(
                wavelet_anomaly
            ),
            "wavelet": self.wavelet,
            "level": self.level,
        }
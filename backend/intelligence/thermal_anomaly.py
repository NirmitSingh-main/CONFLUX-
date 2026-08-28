import cv2
import numpy as np


class ThermalAnomalyDetector:
    """
    Detect thermal anomalies in infrared imagery.

    This baseline uses statistical hotspot detection.
    Later, a trained vision model can replace or complement
    this detector without changing the rest of the architecture.
    """

    def __init__(
        self,
        threshold_factor: float = 2.5,
        hotspot_ratio_threshold: float = 0.01,
    ):
        self.threshold_factor = threshold_factor
        self.hotspot_ratio_threshold = hotspot_ratio_threshold

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Convert an input image into a grayscale thermal representation."""

        if image is None:
            raise ValueError("Image cannot be None.")

        if not isinstance(image, np.ndarray):
            raise TypeError("Image must be a NumPy array.")

        if image.size == 0:
            raise ValueError("Image cannot be empty.")

        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        return image.astype(np.float32)

    def detect(self, image: np.ndarray) -> dict:
        """
        Detect statistically unusual thermal regions.

        Returns:
            Dictionary containing thermal statistics and anomaly information.
        """

        thermal_image = self.preprocess(image)

        mean_intensity = float(np.mean(thermal_image))
        standard_deviation = float(np.std(thermal_image))

        threshold = (
            mean_intensity
            + self.threshold_factor * standard_deviation
        )

        hotspot_mask = thermal_image > threshold

        hotspot_pixels = int(np.sum(hotspot_mask))
        total_pixels = int(thermal_image.size)

        hotspot_ratio = hotspot_pixels / total_pixels

        anomaly_detected = (
            hotspot_ratio >= self.hotspot_ratio_threshold
        )

        # Find the location of the hottest pixel.
        hottest_index = np.unravel_index(
            np.argmax(thermal_image),
            thermal_image.shape,
        )

        hottest_value = float(
            thermal_image[hottest_index]
        )

        return {
            "anomaly_detected": anomaly_detected,
            "mean_intensity": mean_intensity,
            "standard_deviation": standard_deviation,
            "threshold": float(threshold),
            "hottest_intensity": hottest_value,
            "hottest_location": {
                "y": int(hottest_index[0]),
                "x": int(hottest_index[1]),
            },
            "hotspot_pixels": hotspot_pixels,
            "hotspot_ratio": float(hotspot_ratio),
        }
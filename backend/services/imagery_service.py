import cv2
import numpy as np
from backend.intelligence.thermal_anomaly import ThermalAnomalyDetector


class ImageryService:
    """
    Service responsible for processing spacecraft radiometric frames
    and detecting thermal hotspot anomalies.
    """

    def __init__(
        self,
        threshold_factor: float = 2.5,
        hotspot_ratio_threshold: float = 0.01,
    ):
        self.detector = ThermalAnomalyDetector(
            threshold_factor=threshold_factor,
            hotspot_ratio_threshold=hotspot_ratio_threshold,
        )

    def analyze_image_bytes(self, image_bytes: bytes) -> dict:
        if not image_bytes:
            raise ValueError("Image bytes cannot be empty.")

        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Unable to decode valid image from provided bytes.")

        return self.detector.detect(image)

    def analyze_image_matrix(self, image: np.ndarray) -> dict:
        return self.detector.detect(image)

from pathlib import Path
import sys

import cv2

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from backend.intelligence.thermal_anomaly import (
    ThermalAnomalyDetector,
)


IMAGE_DIR = Path(
    "data/infrared/infrared"
)


def main() -> None:

    print("Loading infrared dataset...")

    if not IMAGE_DIR.exists():
        raise FileNotFoundError(
            f"Infrared dataset not found: {IMAGE_DIR}"
        )

    image_paths = sorted(
        IMAGE_DIR.glob("*.png")
    )

    if not image_paths:
        raise FileNotFoundError(
            f"No PNG images found in {IMAGE_DIR}"
        )

    print(
        f"Found {len(image_paths)} infrared images."
    )

    detector = ThermalAnomalyDetector(
        threshold_factor=2.5,
        hotspot_ratio_threshold=0.01,
    )

    detected_count = 0

    print("\nAnalyzing infrared images...")

    for image_path in image_paths:

        image = cv2.imread(
            str(image_path),
            cv2.IMREAD_UNCHANGED,
        )

        if image is None:
            print(
                f"Warning: could not read "
                f"{image_path.name}"
            )
            continue

        result = detector.detect(
            image
        )

        if result["anomaly_detected"]:
            detected_count += 1

            print(
                f"[ANOMALY] "
                f"{image_path.name} | "
                f"hotspot ratio: "
                f"{result['hotspot_ratio']:.4f} | "
                f"hottest: "
                f"{result['hottest_intensity']:.2f}"
            )

    print("\nInfrared analysis complete.")

    print(
        f"Images analyzed: "
        f"{len(image_paths)}"
    )

    print(
        f"Thermal anomalies detected: "
        f"{detected_count}"
    )

    print(
        f"Normal images: "
        f"{len(image_paths) - detected_count}"
    )


if __name__ == "__main__":
    main()
from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from backend.intelligence.wavefront_anomaly import (
    WavefrontAnomalyDetector,
)


DATASET_PATH = Path(
    "data/wavefront/wavefront_dataset_500.csv"
)

MODEL_PATH = Path(
    "models/wavefront_detector.pkl"
)

FEATURES = [
    "wavefront_rms_um",
    "tip_error_um",
    "tilt_error_um",
    "defocus_um",
    "astigmatism_um",
    "coma_um",
]


def load_dataset() -> pd.DataFrame:

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    data = pd.read_csv(
        DATASET_PATH
    )

    required = FEATURES + [
        "is_anomaly"
    ]

    missing = [
        column
        for column in required
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    return data


def main() -> None:

    print(
        "Loading wavefront dataset..."
    )

    data = load_dataset()

    print(
        f"Loaded {len(data)} wavefront samples."
    )

    normal_data = data[
        data["is_anomaly"] == 0
    ]

    print(
        f"Normal samples: {len(normal_data)}"
    )

    print(
        f"Known anomalies: "
        f"{data['is_anomaly'].sum()}"
    )

    # ---------------------------------------------
    # Train only on normal observations.
    # ---------------------------------------------

    normal_features = normal_data[
        FEATURES
    ].to_numpy(
        dtype=float
    )

    detector = WavefrontAnomalyDetector(
        wavelet="db4",
        level=2,
        threshold=3.0,
    )

    print(
        "\nTraining wavefront detector..."
    )

    detector.fit(
        normal_features
    )

    print(
        "Training complete."
    )

    print(
        f"Baseline energy: "
        f"{detector.baseline_energy:.6f}"
    )

    # ---------------------------------------------
    # Evaluate.
    # ---------------------------------------------

    predictions = []

    all_features = data[
        FEATURES
    ].to_numpy(
        dtype=float
    )

    for row in all_features:

        result = detector.analyze(
            row
        )

        predictions.append(
            int(
                result["anomaly_detected"]
            )
        )

    actual = data[
        "is_anomaly"
    ].to_numpy(
        dtype=int
    )

    predictions = np.asarray(
        predictions,
        dtype=int
    )

    true_positive = int(
        np.sum(
            (actual == 1)
            & (predictions == 1)
        )
    )

    false_positive = int(
        np.sum(
            (actual == 0)
            & (predictions == 1)
        )
    )

    false_negative = int(
        np.sum(
            (actual == 1)
            & (predictions == 0)
        )
    )

    correct = int(
        np.sum(
            actual == predictions
        )
    )

    accuracy = (
        correct / len(actual)
    )

    precision = (
        true_positive
        / max(
            true_positive
            + false_positive,
            1,
        )
    )

    recall = (
        true_positive
        / max(
            true_positive
            + false_negative,
            1,
        )
    )

    f1 = (
        2
        * precision
        * recall
        / max(
            precision + recall,
            1e-12,
        )
    )

    print(
        "\nEvaluation:"
    )

    print(
        f"Correct predictions: "
        f"{correct}/{len(actual)}"
    )

    print(
        f"Accuracy: {accuracy:.2%}"
    )

    print(
        f"Precision: {precision:.2%}"
    )

    print(
        f"Recall: {recall:.2%}"
    )

    print(
        f"F1 Score: {f1:.2f}"
    )

    print(
        f"Actual anomalies: "
        f"{actual.sum()}"
    )

    print(
        f"Detected anomalies: "
        f"{predictions.sum()}"
    )

    # ---------------------------------------------
    # Save detector.
    # ---------------------------------------------

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        detector,
        MODEL_PATH,
    )

    print(
        f"\nModel saved to: {MODEL_PATH}"
    )


if __name__ == "__main__":
    main()
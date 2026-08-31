from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import IsolationForest


FEATURES = [
    "temperature",
    "voltage",
    "current",
    "battery",
    "pressure",
    "vibration",
]

DATASET_PATH = Path(
    "data/telemetry/telemetry_dataset_500.csv"
)

MODEL_PATH = Path(
    "models/telemetry_isolation_forest.joblib"
)


def load_dataset() -> pd.DataFrame:
    """Load the telemetry dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    data = pd.read_csv(DATASET_PATH)

    missing = [
        feature
        for feature in FEATURES
        if feature not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing telemetry features: {missing}"
        )

    return data


def train_model(
    data: pd.DataFrame,
) -> IsolationForest:
    """
    Train Isolation Forest using telemetry features.

    Ground-truth labels are deliberately NOT used for training.
    """

    X = data[FEATURES].to_numpy(dtype=float)

    model = IsolationForest(
        contamination=0.10,
        random_state=42,
        n_estimators=200,
    )

    model.fit(X)

    return model


def evaluate_model(
    model: IsolationForest,
    data: pd.DataFrame,
) -> None:
    """
    Evaluate predictions against the known synthetic labels.
    """

    X = data[FEATURES].to_numpy(dtype=float)

    predictions = model.predict(X)

    # Isolation Forest:
    #  1  = normal
    # -1  = anomaly
    predicted_anomaly = (
        predictions == -1
    ).astype(int)

    actual_anomaly = data[
        "is_anomaly"
    ].to_numpy(dtype=int)

    print("\nConfusion Matrix:")
    print(
        confusion_matrix(
            actual_anomaly,
            predicted_anomaly,
        )
    )

    print("\nClassification Report:")
    print(
        classification_report(
            actual_anomaly,
            predicted_anomaly,
            target_names=[
                "Normal",
                "Anomaly",
            ],
            zero_division=0,
        )
    )


def save_model(
    model: IsolationForest,
) -> None:
    """Save the trained model."""

    import joblib

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print(
        f"\nModel saved to: {MODEL_PATH}"
    )


def main() -> None:

    print("Loading telemetry dataset...")

    data = load_dataset()

    print(
        f"Loaded {len(data)} telemetry samples."
    )

    print(
        f"Known anomalies: "
        f"{data['is_anomaly'].sum()}"
    )

    print("\nTraining Isolation Forest...")

    model = train_model(data)

    print("Training complete.")

    evaluate_model(
        model,
        data,
    )

    save_model(model)


if __name__ == "__main__":
    main()
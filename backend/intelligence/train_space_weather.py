from pathlib import Path
import sys

import pandas as pd

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from backend.intelligence.space_weather import (
    SpaceWeatherAnalyzer,
)


DATASET_PATH = Path(
    "data/space_weather/space_weather_dataset_500.csv"
)


def load_dataset() -> pd.DataFrame:
    """Load and validate the space-weather dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    data = pd.read_csv(
        DATASET_PATH
    )

    required_columns = [
        "kp_index",
        "solar_wind_speed_km_s",
        "proton_density_cm3",
        "bz_nt",
        "xray_log_flux",
        "environmental_anomaly",
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    return data


def main() -> None:

    print(
        "Loading space-weather dataset..."
    )

    data = load_dataset()

    print(
        f"Loaded {len(data)} space-weather samples."
    )

    print(
        f"Known anomalies: "
        f"{data['environmental_anomaly'].sum()}"
    )

    # ------------------------------------------------
    # Determine thresholds from the normal baseline.
    # ------------------------------------------------

    normal_data = data[
        data["environmental_anomaly"] == 0
    ]

    if len(normal_data) == 0:
        raise ValueError(
            "No normal space-weather samples found."
        )

    # Thresholds are learned from the upper normal range.
    kp_threshold = normal_data[
        "kp_index"
    ].quantile(0.99)

    solar_wind_threshold = normal_data[
        "solar_wind_speed_km_s"
    ].quantile(0.99)

    proton_density_threshold = normal_data[
        "proton_density_cm3"
    ].quantile(0.99)

    xray_threshold = normal_data[
        "xray_log_flux"
    ].quantile(0.99)

    # Bz can be positive or negative.
    # Strong negative Bz is particularly relevant
    # for geomagnetic activity.
    bz_threshold = normal_data[
        "bz_nt"
    ].quantile(0.01)

    # ------------------------------------------------
    # Create analyzer.
    # ------------------------------------------------

    analyzer = SpaceWeatherAnalyzer(
        solar_activity_threshold=float(
            solar_wind_threshold
        ),
        radiation_threshold=float(
            proton_density_threshold
        ),
        geomagnetic_activity_threshold=float(
            kp_threshold
        ),
    )

    print("\nLearned thresholds:")

    print(
        f"Solar-wind threshold: "
        f"{solar_wind_threshold:.3f}"
    )

    print(
        f"Proton-density threshold: "
        f"{proton_density_threshold:.3f}"
    )

    print(
        f"Kp threshold: "
        f"{kp_threshold:.3f}"
    )

    print(
        f"X-ray threshold: "
        f"{xray_threshold:.3f}"
    )

    print(
        f"Bz lower threshold: "
        f"{bz_threshold:.3f}"
    )

    # ------------------------------------------------
    # Evaluate.
    # ------------------------------------------------

    predictions = []

    for _, row in data.iterrows():

        # Solar activity is represented by solar-wind speed.
        solar_activity = float(
            row["solar_wind_speed_km_s"]
        )

        # Radiation/environmental particle activity.
        radiation_level = float(
            row["proton_density_cm3"]
        )

        # Geomagnetic activity.
        geomagnetic_activity = float(
            row["kp_index"]
        )

        result = analyzer.analyze(
            solar_activity=solar_activity,
            radiation_level=radiation_level,
            geomagnetic_activity=geomagnetic_activity,
        )

        # Include X-ray activity and strong negative Bz
        # as additional environmental indicators.
        xray_event = (
            float(row["xray_log_flux"])
            >= xray_threshold
        )

        strong_negative_bz = (
            float(row["bz_nt"])
            <= bz_threshold
        )

        anomaly_detected = (
            result["environmental_anomaly"]
            or xray_event
            or strong_negative_bz
        )

        predictions.append(
            int(anomaly_detected)
        )

    actual = data[
        "environmental_anomaly"
    ].to_numpy(
        dtype=int
    )

    true_positive = sum(
        1
        for a, p in zip(actual, predictions)
        if a == 1 and p == 1
    )

    false_positive = sum(
        1
        for a, p in zip(actual, predictions)
        if a == 0 and p == 1
    )

    false_negative = sum(
        1
        for a, p in zip(actual, predictions)
        if a == 1 and p == 0
    )

    correct = sum(
        a == p
        for a, p in zip(actual, predictions)
    )

    accuracy = (
        correct / len(actual)
    )

    precision = (
        true_positive
        / max(
            true_positive + false_positive,
            1,
        )
    )

    recall = (
        true_positive
        / max(
            true_positive + false_negative,
            1,
        )
    )

    f1 = (
        2 * precision * recall
        / max(
            precision + recall,
            1e-12,
        )
    )

    print("\nEvaluation:")

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
        f"{sum(actual)}"
    )

    print(
        f"Detected anomalies: "
        f"{sum(predictions)}"
    )

    print("\nSpace-weather analysis complete.")


if __name__ == "__main__":
    main()
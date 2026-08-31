from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
N_SAMPLES = 500
N_ANOMALIES = 50


def generate_wavefront_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)

    timestamps = pd.date_range(
        start="2026-08-29 00:00:00",
        periods=N_SAMPLES,
        freq="1min",
    )

    # Normal wavefront measurements
    wavefront_rms = rng.normal(
        loc=0.08,
        scale=0.01,
        size=N_SAMPLES,
    )

    tip_error = rng.normal(
        loc=0.0,
        scale=0.01,
        size=N_SAMPLES,
    )

    tilt_error = rng.normal(
        loc=0.0,
        scale=0.01,
        size=N_SAMPLES,
    )

    defocus = rng.normal(
        loc=0.0,
        scale=0.015,
        size=N_SAMPLES,
    )

    astigmatism = rng.normal(
        loc=0.0,
        scale=0.01,
        size=N_SAMPLES,
    )

    coma = rng.normal(
        loc=0.0,
        scale=0.008,
        size=N_SAMPLES,
    )

    is_anomaly = np.zeros(
        N_SAMPLES,
        dtype=int,
    )

    anomaly_type = np.array(
        ["NONE"] * N_SAMPLES,
        dtype=object,
    )

    # Exactly 50 anomalous observations.
    anomaly_indices = rng.choice(
        N_SAMPLES,
        size=N_ANOMALIES,
        replace=False,
    )

    for index in anomaly_indices:

        anomaly_type[index] = rng.choice(
            [
                "WAVEFRONT_DISTORTION",
                "TIP_TILT_ERROR",
                "DEFOCUS",
                "ASTIGMATISM",
                "COMA",
            ]
        )

        is_anomaly[index] = 1

        if anomaly_type[index] == "WAVEFRONT_DISTORTION":
            wavefront_rms[index] = rng.uniform(
                0.18,
                0.30,
            )

        elif anomaly_type[index] == "TIP_TILT_ERROR":
            tip_error[index] = rng.uniform(
                0.08,
                0.15,
            )

            tilt_error[index] = rng.uniform(
                0.08,
                0.15,
            )

        elif anomaly_type[index] == "DEFOCUS":
            defocus[index] = rng.uniform(
                0.12,
                0.22,
            )

        elif anomaly_type[index] == "ASTIGMATISM":
            astigmatism[index] = rng.uniform(
                0.10,
                0.18,
            )

        elif anomaly_type[index] == "COMA":
            coma[index] = rng.uniform(
                0.08,
                0.15,
            )

    data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "wavefront_rms_um": np.round(
                wavefront_rms,
                5,
            ),
            "tip_error_um": np.round(
                tip_error,
                5,
            ),
            "tilt_error_um": np.round(
                tilt_error,
                5,
            ),
            "defocus_um": np.round(
                defocus,
                5,
            ),
            "astigmatism_um": np.round(
                astigmatism,
                5,
            ),
            "coma_um": np.round(
                coma,
                5,
            ),
            "is_anomaly": is_anomaly,
            "anomaly_type": anomaly_type,
        }
    )

    return data


def main() -> None:

    output_path = Path(
        "data/wavefront/wavefront_dataset_500.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = generate_wavefront_dataset()

    data.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Dataset created: {output_path}"
    )

    print(
        f"Total samples: {len(data)}"
    )

    print(
        f"Normal samples: "
        f"{(data['is_anomaly'] == 0).sum()}"
    )

    print(
        f"Anomalous samples: "
        f"{(data['is_anomaly'] == 1).sum()}"
    )

    print("\nAnomaly types:")

    print(
        data[
            data["is_anomaly"] == 1
        ]["anomaly_type"].value_counts()
    )


if __name__ == "__main__":
    main()
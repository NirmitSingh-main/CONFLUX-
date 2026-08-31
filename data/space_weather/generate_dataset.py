from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
N_SAMPLES = 500
N_ANOMALIES = 50


def generate_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)

    timestamps = pd.date_range(
        start="2026-08-29 00:00:00",
        periods=N_SAMPLES,
        freq="1min",
    )

    # -------------------------------------------------
    # Normal space-weather conditions
    # -------------------------------------------------

    kp_index = rng.normal(
        loc=2.0,
        scale=0.7,
        size=N_SAMPLES,
    )

    solar_wind_speed = rng.normal(
        loc=400.0,
        scale=45.0,
        size=N_SAMPLES,
    )

    proton_density = rng.normal(
        loc=5.0,
        scale=1.2,
        size=N_SAMPLES,
    )

    bz_nt = rng.normal(
        loc=1.0,
        scale=2.5,
        size=N_SAMPLES,
    )

    xray_log_flux = rng.normal(
        loc=-6.0,
        scale=0.4,
        size=N_SAMPLES,
    )

    # Keep normal values physically sensible.
    kp_index = np.clip(
        kp_index,
        0,
        9,
    )

    solar_wind_speed = np.clip(
        solar_wind_speed,
        250,
        600,
    )

    proton_density = np.clip(
        proton_density,
        0.5,
        12,
    )

    bz_nt = np.clip(
        bz_nt,
        -8,
        8,
    )

    xray_log_flux = np.clip(
        xray_log_flux,
        -7,
        -4,
    )

    environmental_anomaly = np.zeros(
        N_SAMPLES,
        dtype=int,
    )

    anomaly_type = np.array(
        ["NONE"] * N_SAMPLES,
        dtype=object,
    )

    # -------------------------------------------------
    # Inject exactly 50 anomalies.
    # -------------------------------------------------

    anomaly_indices = rng.choice(
        N_SAMPLES,
        size=N_ANOMALIES,
        replace=False,
    )

    anomaly_types = [
        "SOLAR_STORM",
        "RADIATION_EVENT",
        "GEOMAGNETIC_STORM",
        "XRAY_EVENT",
        "COMBINED_STORM",
    ]

    for index in anomaly_indices:

        anomaly_type[index] = rng.choice(
            anomaly_types
        )

        environmental_anomaly[index] = 1

        if anomaly_type[index] == "SOLAR_STORM":

            solar_wind_speed[index] = rng.uniform(
                650,
                850,
            )

            proton_density[index] = rng.uniform(
                10,
                18,
            )

        elif anomaly_type[index] == "RADIATION_EVENT":

            proton_density[index] = rng.uniform(
                15,
                25,
            )

            solar_wind_speed[index] = rng.uniform(
                550,
                750,
            )

        elif anomaly_type[index] == "GEOMAGNETIC_STORM":

            kp_index[index] = rng.uniform(
                6,
                9,
            )

            bz_nt[index] = rng.uniform(
                -15,
                -8,
            )

        elif anomaly_type[index] == "XRAY_EVENT":

            xray_log_flux[index] = rng.uniform(
                -3.5,
                -2.0,
            )

        elif anomaly_type[index] == "COMBINED_STORM":

            kp_index[index] = rng.uniform(
                6,
                9,
            )

            solar_wind_speed[index] = rng.uniform(
                650,
                900,
            )

            proton_density[index] = rng.uniform(
                12,
                25,
            )

            bz_nt[index] = rng.uniform(
                -18,
                -9,
            )

            xray_log_flux[index] = rng.uniform(
                -4,
                -2,
            )

    data = pd.DataFrame(
        {
            "timestamp": timestamps,

            "kp_index": np.round(
                kp_index,
                3,
            ),

            "solar_wind_speed_km_s": np.round(
                solar_wind_speed,
                3,
            ),

            "proton_density_cm3": np.round(
                proton_density,
                3,
            ),

            "bz_nt": np.round(
                bz_nt,
                3,
            ),

            "xray_log_flux": np.round(
                xray_log_flux,
                3,
            ),

            "environmental_anomaly":
                environmental_anomaly,

            "anomaly_type":
                anomaly_type,
        }
    )

    return data


def main() -> None:

    output_path = Path(
        "data/space_weather/"
        "space_weather_dataset_500.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = generate_dataset()

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
        "Normal samples: "
        f"{(data['environmental_anomaly'] == 0).sum()}"
    )

    print(
        "Anomalous samples: "
        f"{(data['environmental_anomaly'] == 1).sum()}"
    )

    print("\nAnomaly types:")

    print(
        data[
            data["environmental_anomaly"] == 1
        ]["anomaly_type"].value_counts()
    )


if __name__ == "__main__":
    main()
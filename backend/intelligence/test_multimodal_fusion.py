from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from backend.intelligence.multimodal_fusion import (
    MultimodalFusion,
)


def main() -> None:

    fusion = MultimodalFusion()

    telemetry_result = {
        "anomaly_detected": True,
        "anomaly_score": -0.12,
    }

    thermal_result = {
        "anomaly_detected": False,
        "mean_intensity": 82.4,
        "hotspot_ratio": 0.004,
    }

    wavefront_result = {
        "anomaly_detected": True,
        "anomaly_score": 1.0,
        "max_z_score": 4.7,
    }

    orbital_result = {
        "collision_risk": False,
    }

    space_weather_result = {
        "environmental_anomaly": True,
        "active_events": [
            "ELEVATED_SOLAR_ACTIVITY",
        ],
    }

    result = fusion.fuse(
        telemetry=telemetry_result,
        thermal=thermal_result,
        wavelet=wavefront_result,
        orbital=orbital_result,
        space_weather=space_weather_result,
    )

    print("Multimodal Fusion Test")
    print("======================")

    print(
        "\nAvailable modalities:"
    )
    print(
        result["available_modalities"]
    )

    print(
        "\nAnomalous modalities:"
    )
    print(
        result["anomalous_modalities"]
    )

    print(
        "\nNormal modalities:"
    )
    print(
        result["normal_modalities"]
    )

    print(
        "\nAnomaly count:"
    )
    print(
        result["anomaly_count"]
    )

    print(
        "\nMulti-modal agreement:"
    )
    print(
        result["multi_modal_agreement"]
    )


if __name__ == "__main__":
    main()
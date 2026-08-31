from typing import Any


class CopilotService:
    """
    Service responsible for synthesizing mission intelligence states into
    operational recommendations and operator advisory insights.
    """

    @staticmethod
    def generate_mission_advisory(
        mission_id: int,
        modality_state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate operational recommendations based on detected anomalies.
        """
        recommendations = []
        severity = "NOMINAL"

        # Check telemetry
        if modality_state.get("telemetry_anomaly"):
            recommendations.append(
                "Subsystem telemetry anomaly detected: Review power distribution and bus pressure logs."
            )
            severity = "WARNING"

        # Check thermal
        if modality_state.get("thermal_anomaly"):
            recommendations.append(
                "Thermal hotspot detected: Activate secondary radiator loop and reorient spacecraft sun-angle."
            )
            severity = "WARNING"

        # Check wavefront
        if modality_state.get("wavefront_anomaly"):
            recommendations.append(
                "Optical wavefront aberration detected: Perform decenter calibration on primary mirror actuators."
            )
            severity = "WARNING"

        # Check orbital
        orbital_status = modality_state.get("orbital_status", "NOMINAL")
        if orbital_status in {"WARNING", "CRITICAL"}:
            recommendations.append(
                f"Orbital conjunction alert ({orbital_status}): Prepare delta-V avoidance burn maneuver sequence."
            )
            severity = "CRITICAL" if orbital_status == "CRITICAL" else "WARNING"

        # Check space weather
        if modality_state.get("space_weather_anomaly"):
            recommendations.append(
                "Elevated space weather flux detected: Engage radiation hardening protocol and star tracker shielding."
            )
            severity = "WARNING" if severity != "CRITICAL" else severity

        # Multimodal correlation
        if len(recommendations) >= 3:
            severity = "CRITICAL"
            recommendations.insert(
                0,
                "MULTIMODAL CORRELATION ALERT: Multiple subsystems show simultaneous divergence. Initiate automated safe-hold mode assessment.",
            )

        if not recommendations:
            recommendations.append("All spacecraft subsystems and environmental factors remain nominal.")

        return {
            "mission_id": mission_id,
            "severity": severity,
            "actionable_recommendations": recommendations,
            "anomaly_count": len(
                [
                    k
                    for k, v in modality_state.items()
                    if v is True or v in {"WARNING", "CRITICAL"}
                ]
            ),
        }

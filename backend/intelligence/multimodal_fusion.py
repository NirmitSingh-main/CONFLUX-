from typing import Any


class MultimodalFusion:
    """
    CONFLUX Multimodal Fusion Engine.

    Consumes the latest per-modality analysis results and produces a
    structured mission-level assessment with:
    - Which modalities are anomalous / normal / unavailable
    - Cross-modal correlation analysis
    - Primary mission problem identification
    - Overall severity and risk level
    - Deterministic confidence scoring
    - Recommended operator action

    No random values are generated.  All outputs are derived from the
    authoritative analysis results passed as inputs.
    """

    # --------------------------------------------------
    # Anomaly detection helpers
    # --------------------------------------------------

    def _contains_anomaly(self, result: dict[str, Any]) -> bool:
        """Determine whether a modality analysis reports an abnormal state."""

        # Telemetry / Wavefront / Thermal (direct anomaly flag)
        if result.get("anomaly_detected") is True:
            return True

        # Space Weather
        if result.get("environmental_anomaly") is True:
            return True

        # Orbital
        if result.get("collision_risk") is True:
            return True

        # Modules using explicit status values
        if result.get("status") in {"WARNING", "CRITICAL", "ANOMALOUS", "ENVIRONMENTAL_ANOMALY"}:
            return True

        # Risk-level based
        if result.get("risk_level") in {"HIGH", "CRITICAL"}:
            return True

        return False

    def _get_orbital_risk(self, orbital: dict[str, Any] | None) -> str:
        """Return the orbital risk level: NOMINAL / WARNING / CRITICAL."""
        if orbital is None:
            return "UNAVAILABLE"
        if orbital.get("collision_risk") or orbital.get("status") == "CRITICAL":
            return "CRITICAL"
        if orbital.get("status") == "WARNING" or orbital.get("risk_level") in {"HIGH", "CRITICAL"}:
            return "WARNING"
        return "NOMINAL"

    # --------------------------------------------------
    # Correlation logic
    # --------------------------------------------------

    def _correlate(
        self,
        anomalous: list[str],
        normal: list[str],
        unavailable: list[str],
        orbital_risk: str,
    ) -> tuple[list[str], str, str, str, str]:
        """
        Deterministic rule-based cross-modal correlation.

        Returns:
            (correlated_events, primary_problem, severity, risk_level, explanation, recommended_action)
        """

        a = set(anomalous)
        n = set(normal)

        # Rule 1: No anomalies at all
        if not a:
            return (
                [],
                "No significant cross-modal anomaly detected",
                "LOW",
                "LOW",
                (
                    "All evaluated modalities report nominal conditions. "
                    "No correlated anomalies identified."
                ),
                "Continue nominal operations. Maintain routine monitoring cadence.",
            )

        correlated_events: list[str] = []

        # Rule 2: Orbital critical + other anomalies
        if orbital_risk == "CRITICAL" and len(a) > 1:
            correlated_events.append("ORBITAL_COLLISION_RISK_WITH_SUPPORTING_ANOMALIES")
            return (
                correlated_events,
                "Orbital collision risk with corroborating multi-modal anomalies",
                "CRITICAL",
                "CRITICAL",
                (
                    "A critical orbital close-approach event is detected alongside "
                    f"additional anomalies in: {', '.join(a - {'orbital'})}. "
                    "This represents a combined operational hazard."
                ),
                "Immediate maneuver assessment required. Escalate to mission operations. "
                "Evaluate evasive maneuver options before time-to-closest-approach expires.",
            )

        # Rule 3: Orbital critical alone
        if orbital_risk == "CRITICAL":
            correlated_events.append("ORBITAL_COLLISION_RISK")
            return (
                correlated_events,
                "Orbital close approach / collision risk",
                "HIGH",
                "CRITICAL",
                (
                    "A critical orbital conjunction has been detected. "
                    "The calculated miss distance breaches the safety threshold. "
                    "Other modalities are nominal."
                ),
                "Evaluate orbital maneuver options immediately. "
                "Verify tracking data and compute conjunction probability. "
                "Notify flight dynamics team.",
            )

        # Rule 4: Space weather + telemetry + thermal (all three → environmental/subsystem cascade)
        if "space_weather" in a and "telemetry" in a and "thermal" in a:
            correlated_events.extend([
                "ELEVATED_SPACE_WEATHER",
                "TELEMETRY_ANOMALY",
                "THERMAL_ANOMALY",
                "POSSIBLE_ENVIRONMENTAL_SUBSYSTEM_CASCADE",
            ])
            return (
                correlated_events,
                "Potential environmental-driven subsystem anomaly cascade",
                "HIGH",
                "HIGH",
                (
                    "Space weather anomaly detected concurrently with both telemetry and thermal anomalies. "
                    "Elevated environmental flux may be inducing subsystem disturbances. "
                    "Cross-modal correlation suggests a possible environmental cascade event."
                ),
                "Investigate spacecraft radiation shielding and thermal margins. "
                "Cross-correlate telemetry anomalies with space-weather event timestamps. "
                "Consider increased monitoring frequency and prepare contingency thermal control actions.",
            )

        # Rule 5: Telemetry + thermal (subsystem/thermal coupling)
        if "telemetry" in a and "thermal" in a:
            correlated_events.extend(["TELEMETRY_ANOMALY", "THERMAL_ANOMALY", "POSSIBLE_SUBSYSTEM_THERMAL_COUPLING"])
            wavefront_note = ""
            if "wavelet" in a or "wavefront" in a:
                correlated_events.append("OPTICAL_ANOMALY")
                wavefront_note = " Optical wavefront anomaly may indicate structural or thermal distortion of optical elements."
            severity = "HIGH" if len(a) >= 3 else "MEDIUM"
            return (
                correlated_events,
                "Correlated thermal and telemetry subsystem anomaly",
                severity,
                severity,
                (
                    "Concurrent anomalies in telemetry and thermal channels suggest a "
                    f"potential subsystem heating or power anomaly.{wavefront_note} "
                    f"Orbital and space-weather conditions are {'nominal' if not ({'orbital','space_weather'} & a) else 'also anomalous'}."
                ),
                "Correlate thermal hotspot location with affected subsystem. "
                "Review power consumption telemetry and thermal control system status. "
                "Check for thermal runaway indicators.",
            )

        # Rule 6: Space weather + telemetry (environmental influence on electronics)
        if "space_weather" in a and "telemetry" in a:
            correlated_events.extend(["ELEVATED_SPACE_WEATHER", "TELEMETRY_ANOMALY", "POSSIBLE_RADIATION_EFFECT"])
            return (
                correlated_events,
                "Environmental space-weather disturbance with telemetry correlation",
                "MEDIUM",
                "MEDIUM",
                (
                    "Elevated space-weather conditions coincide with a telemetry anomaly. "
                    "Ionizing radiation or geomagnetic disturbance may be affecting spacecraft electronics."
                ),
                "Monitor telemetry evolution relative to space-weather event timeline. "
                "Verify safe mode and autonomous fault management responses. "
                "Increase radiation monitoring cadence.",
            )

        # Rule 7: Space weather + thermal
        if "space_weather" in a and "thermal" in a:
            correlated_events.extend(["ELEVATED_SPACE_WEATHER", "THERMAL_ANOMALY"])
            return (
                correlated_events,
                "Space weather disturbance with thermal correlation",
                "MEDIUM",
                "MEDIUM",
                (
                    "Elevated environmental flux is correlated with a thermal anomaly. "
                    "Solar heating or particle flux may be affecting spacecraft surface temperatures."
                ),
                "Review thermal model for current solar input flux. "
                "Verify heater setpoints and thermal blanket performance.",
            )

        # Rule 8: Space weather alone
        if "space_weather" in a and len(a) == 1:
            correlated_events.append("ELEVATED_SPACE_WEATHER")
            return (
                correlated_events,
                "Elevated space-weather disturbance (isolated environmental anomaly)",
                "MEDIUM",
                "MEDIUM",
                (
                    "Environmental conditions are elevated but no corroborating spacecraft "
                    "subsystem anomalies have been detected at this time."
                ),
                "Increase monitoring of telemetry and thermal channels. "
                "Review radiation dose accumulation. "
                "Prepare contingency plans for potential equipment anomalies.",
            )

        # Rule 9: Orbital warning (not critical) with other anomalies
        if orbital_risk == "WARNING" and a - {"orbital"}:
            correlated_events.extend(["ORBITAL_WARNING"] + [f"{m.upper()}_ANOMALY" for m in a if m != "orbital"])
            return (
                correlated_events,
                "Orbital close-approach warning with supporting anomalies",
                "HIGH",
                "HIGH",
                (
                    f"Orbital close-approach warning detected alongside anomalies in: "
                    f"{', '.join(a - {'orbital'})}. "
                    "The combination of orbital and subsystem/environmental anomalies "
                    "represents an elevated operational risk."
                ),
                "Prioritise orbital safety assessment. "
                "Verify spacecraft health before any orbital maneuver. "
                "Monitor all anomalous modalities closely.",
            )

        # Rule 10: Orbital warning alone
        if orbital_risk == "WARNING":
            correlated_events.append("ORBITAL_WARNING")
            return (
                correlated_events,
                "Orbital close-approach warning",
                "MEDIUM",
                "MEDIUM",
                (
                    "A close approach has been detected but miss distance remains above the critical threshold. "
                    "No supporting spacecraft subsystem anomalies detected."
                ),
                "Monitor orbital trajectory evolution. "
                "Assess whether a maneuver is required before time-to-closest-approach. "
                "Update conjunction screening with latest tracking data.",
            )

        # Rule 11: Wavefront/optical alone
        if ("wavelet" in a or "wavefront" in a) and len(a) == 1:
            correlated_events.append("OPTICAL_ANOMALY")
            return (
                correlated_events,
                "Optical/wavefront aberration anomaly",
                "MEDIUM",
                "MEDIUM",
                (
                    "A wavefront optical anomaly is detected but is not corroborated by "
                    "thermal or telemetry anomalies. May indicate an isolated optical system issue."
                ),
                "Inspect optical system alignment and focus. "
                "Check for thermal expansion effects on optics mounting. "
                "Review recent pointing and optical performance history.",
            )

        # Rule 12: Telemetry alone
        if "telemetry" in a and len(a) == 1:
            correlated_events.append("TELEMETRY_ANOMALY")
            return (
                correlated_events,
                "Isolated telemetry anomaly",
                "MEDIUM",
                "MEDIUM",
                (
                    "A telemetry anomaly is detected but is not corroborated by "
                    "thermal, optical, orbital, or space-weather anomalies."
                ),
                "Review individual sensor channels for the anomalous readings. "
                "Verify sensor calibration and cross-check with redundant sensors. "
                "Investigate for potential transient sensor fault.",
            )

        # Rule 13: Thermal alone
        if "thermal" in a and len(a) == 1:
            correlated_events.append("THERMAL_ANOMALY")
            return (
                correlated_events,
                "Isolated thermal/infrared anomaly",
                "MEDIUM",
                "MEDIUM",
                (
                    "A thermal anomaly is detected but is not corroborated by "
                    "telemetry or environmental anomalies."
                ),
                "Identify the hotspot location and correlate with spacecraft hardware map. "
                "Review thermal control system and heater operations. "
                "Assess whether the anomaly is progressing.",
            )

        # Rule 14: Multiple anomalies without a specific correlated pattern
        if len(a) >= 2:
            correlated_events.extend([f"{m.upper()}_ANOMALY" for m in sorted(a)])
            return (
                correlated_events,
                f"Multiple independent anomalies detected ({', '.join(sorted(a))})",
                "HIGH",
                "HIGH",
                (
                    f"Anomalies detected across {len(a)} modalities: {', '.join(sorted(a))}. "
                    "The pattern does not match a single known correlated failure mode. "
                    "Operator investigation is required to determine root cause."
                ),
                "Conduct systematic review of all anomalous modalities. "
                "Verify whether anomalies share a common timeline. "
                "Escalate to mission operations for integrated assessment.",
            )

        # Rule 15: Single unmatched anomaly
        single = list(a)[0]
        correlated_events.append(f"{single.upper()}_ANOMALY")
        return (
            correlated_events,
            f"Single modality anomaly: {single}",
            "LOW",
            "LOW",
            f"An anomaly is detected in the {single} modality only. No cross-modal correlation found.",
            f"Investigate {single} anomaly in isolation. Monitor other modalities for escalation.",
        )

    # --------------------------------------------------
    # Confidence scoring
    # --------------------------------------------------

    def _compute_confidence(
        self,
        anomalous: list[str],
        normal: list[str],
        unavailable: list[str],
        correlated_events: list[str],
        modality_confidences: dict[str, float],
    ) -> float:
        """
        Deterministic confidence scoring:

        - Starts at base 0.50
        - Each available modality adds coverage
        - Each anomalous modality with high individual confidence adds
        - Cross-modal agreement (2+ anomalous) adds
        - Missing/unavailable modalities subtract
        - Zero available: very low confidence
        """

        available_count = len(anomalous) + len(normal)

        if available_count == 0:
            return 0.10

        # Base coverage from having analyses available
        coverage = min(available_count / 5.0, 1.0) * 0.30  # up to 0.30

        # Per-modality confidence contribution
        indiv_sum = sum(modality_confidences.values())
        indiv_mean = indiv_sum / available_count if available_count > 0 else 0.0
        indiv_contrib = indiv_mean * 0.30  # up to 0.30

        # Agreement bonus: 2+ anomalous modalities corroborate each other
        if len(anomalous) >= 3:
            agreement_bonus = 0.20
        elif len(anomalous) == 2:
            agreement_bonus = 0.10
        else:
            agreement_bonus = 0.0

        # Missing data penalty
        missing_penalty = len(unavailable) * 0.05  # up to 0.25 for 5 missing

        raw = 0.50 + coverage + indiv_contrib + agreement_bonus - missing_penalty
        return round(max(0.10, min(0.99, raw)), 2)

    # --------------------------------------------------
    # Main fusion method
    # --------------------------------------------------

    def fuse(
        self,
        telemetry: dict[str, Any] | None = None,
        thermal: dict[str, Any] | None = None,
        wavelet: dict[str, Any] | None = None,
        orbital: dict[str, Any] | None = None,
        space_weather: dict[str, Any] | None = None,
        wavefront: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Perform multimodal fusion across all available analysis results.

        Returns a structured assessment dictionary with correlation
        analysis, primary problem, severity, confidence, and recommended action.
        """

        canonical_wavefront = wavefront if wavefront is not None else wavelet
        all_modalities = {
            "telemetry": telemetry,
            "thermal": thermal,
            "wavefront": canonical_wavefront,
            "orbital": orbital,
            "space_weather": space_weather,
        }

        available = {k: v for k, v in all_modalities.items() if v is not None}
        unavailable = [k for k, v in all_modalities.items() if v is None]

        anomalous = [k for k, v in available.items() if self._contains_anomaly(v)]
        normal = [k for k, v in available.items() if not self._contains_anomaly(v)]

        orbital_risk = self._get_orbital_risk(orbital)

        # Collect per-modality confidence scores for overall confidence computation
        modality_confidences: dict[str, float] = {}
        for name, result in available.items():
            c = result.get("confidence")
            if isinstance(c, (int, float)) and 0.0 <= c <= 1.0:
                modality_confidences[name] = float(c)
            else:
                # Default confidence if not provided
                modality_confidences[name] = 0.75

        # Run correlation rules
        correlated_events, primary_problem, severity, risk_level, explanation, recommended_action = (
            self._correlate(anomalous, normal, unavailable, orbital_risk)
        )

        confidence = self._compute_confidence(
            anomalous,
            normal,
            unavailable,
            correlated_events,
            modality_confidences,
        )

        # Build per-modality state summary for fusion response, including explicit
        # NOT_ANALYZED states for modalities that were never analyzed in this mission.
        modality_states: dict[str, dict] = {}
        for name in ["telemetry", "thermal", "wavefront", "orbital", "space_weather"]:
            result = available.get(name)
            if result is None:
                modality_states[name] = {
                    "status": "NOT_ANALYZED",
                    "anomaly_detected": False,
                    "severity": "UNKNOWN",
                    "confidence": 0.0,
                }
                continue
            is_anomalous = self._contains_anomaly(result)
            modality_states[name] = {
                "status": result.get("status", "ANOMALOUS" if is_anomalous else "NOMINAL"),
                "anomaly_detected": is_anomalous,
                "severity": result.get("severity", "UNKNOWN"),
                "confidence": modality_confidences.get(name, 0.75),
            }

        return {
            "available_modalities": list(available.keys()),
            "unavailable_modalities": unavailable,
            "anomalous_modalities": anomalous,
            "normal_modalities": normal,
            "anomaly_count": len(anomalous),
            "multi_modal_agreement": len(anomalous) >= 2,
            "modality_states": modality_states,
            "correlated_events": correlated_events,
            "primary_problem": primary_problem,
            "overall_severity": severity,
            "risk_level": risk_level,
            "confidence": confidence,
            "explanation": explanation,
            "recommended_action": recommended_action,
        }

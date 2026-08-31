# Problem Statement & Operational Scope

Modern space missions operate in complex, high-stress, and harsh operational environments. Spacecraft operators are constantly bombarded with heterogeneous, high-frequency telemetry across isolated subsystem monitors.

---

## 1. The Challenge: Fragmented Telemetry & Alarm Fatigue

1. **Siloed Subsystem Telemetry**:
   Power engineers inspect voltage/current, thermal engineers monitor infrared radiators, optics specialists evaluate wavefront Zernike polynomials, orbital flight dynamicists calculate close approaches, and space weather monitors observe solar flux.
2. **Lack of Cross-Modal Synthesis**:
   A single physical event (e.g., a high-energy solar particle storm) can simultaneously induce a thermal expansion aberration in the primary mirror, a voltage spike in the bus battery, and an elevated radiation alarm. In siloed systems, operators see multiple unrelated alarms without knowing the root cause.
3. **High Latency Decision Making**:
   Manual cross-referencing across multiple consoles during time-critical events (e.g. orbital conjunctions or thruster misfires) increases the risk of loss of mission.

---

## 2. The CONFLUX Solution

CONFLUX bridges these siloes with **Continuous Multimodal Mission Intelligence**:
- Standardized REST APIs for each subsystem telemetry stream.
- Unified machine learning anomaly detectors and physical models.
- Centralized Multimodal Fusion engine that synthesizes 5 channels simultaneously to detect cross-modal agreement.
- Persistent SQLite storage for telemetry history, observations, and anomalies.
- Intuitive, low-cognitive-load frontend mission console with dynamic 3D globe visualization and real-time subsystem inspection.

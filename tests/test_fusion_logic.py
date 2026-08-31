import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.intelligence.multimodal_fusion import MultimodalFusion

fusion = MultimodalFusion()


# --------------------------------------------------
# Test helpers
# --------------------------------------------------

def check(test_name: str, result: dict, expected: dict):
    """Assert that result contains the expected key:value pairs."""
    failed = []
    for key, expected_val in expected.items():
        actual_val = result.get(key)
        if callable(expected_val):
            if not expected_val(actual_val):
                failed.append(f"  {key}: check failed (got {actual_val!r})")
        elif actual_val != expected_val:
            failed.append(f"  {key}: expected {expected_val!r}, got {actual_val!r}")
    if failed:
        print(f"[FAIL] {test_name}")
        for f in failed:
            print(f)
        return False
    else:
        print(f"[PASS] {test_name}")
        return True


def run_all():
    passed = 0
    failed = 0

    # --------------------------------------------------
    # TEST 1 - All modalities normal - NOMINAL
    # --------------------------------------------------
    result = fusion.fuse(
        telemetry={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
        thermal={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.85, "severity": "LOW"},
        wavelet={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.80, "severity": "LOW"},
        orbital={"collision_risk": False, "status": "NOMINAL", "risk_level": "LOW", "confidence": 0.95},
        space_weather={"environmental_anomaly": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
    )
    ok = check(
        "TEST 1 — All Modalities Normal",
        result,
        {
            "anomaly_count": 0,
            "overall_severity": "LOW",
            "risk_level": "LOW",
            "primary_problem": "No significant cross-modal anomaly detected",
        }
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # TEST 2 — Telemetry + Thermal anomaly → Correlated subsystem/thermal
    # --------------------------------------------------
    result = fusion.fuse(
        telemetry={"anomaly_detected": True, "status": "ANOMALOUS", "confidence": 0.85, "severity": "HIGH"},
        thermal={"anomaly_detected": True, "status": "ANOMALOUS", "confidence": 0.88, "severity": "HIGH"},
        wavelet={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.80, "severity": "LOW"},
        orbital={"collision_risk": False, "status": "NOMINAL", "risk_level": "LOW", "confidence": 0.95},
        space_weather={"environmental_anomaly": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
    )
    ok = check(
        "TEST 2 — Telemetry + Thermal Anomaly",
        result,
        {
            "anomaly_count": 2,
            "multi_modal_agreement": True,
            "primary_problem": "Correlated thermal and telemetry subsystem anomaly",
        }
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # TEST 3 — Space Weather + Telemetry + Thermal → environmental cascade
    # --------------------------------------------------
    result = fusion.fuse(
        telemetry={"anomaly_detected": True, "status": "ANOMALOUS", "confidence": 0.82, "severity": "HIGH"},
        thermal={"anomaly_detected": True, "status": "ANOMALOUS", "confidence": 0.88, "severity": "HIGH"},
        wavelet={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.80, "severity": "LOW"},
        orbital={"collision_risk": False, "status": "NOMINAL", "risk_level": "LOW", "confidence": 0.95},
        space_weather={"environmental_anomaly": True, "status": "ENVIRONMENTAL_ANOMALY", "confidence": 0.90, "severity": "HIGH"},
    )
    ok = check(
        "TEST 3 — Space Weather + Telemetry + Thermal (Environmental Cascade)",
        result,
        {
            "anomaly_count": 3,
            "primary_problem": "Potential environmental-driven subsystem anomaly cascade",
            "overall_severity": "HIGH",
        }
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # TEST 4 — Orbital CRITICAL alone
    # --------------------------------------------------
    result = fusion.fuse(
        telemetry={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
        thermal={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.85, "severity": "LOW"},
        wavelet={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.80, "severity": "LOW"},
        orbital={"collision_risk": True, "status": "CRITICAL", "risk_level": "CRITICAL", "confidence": 0.95},
        space_weather={"environmental_anomaly": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
    )
    ok = check(
        "TEST 4 — Orbital Critical Alone",
        result,
        {
            "anomaly_count": 1,
            "risk_level": "CRITICAL",
            "primary_problem": "Orbital close approach / collision risk",
        }
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # TEST 5 — Orbital CRITICAL + other anomalies → combined hazard
    # --------------------------------------------------
    result = fusion.fuse(
        telemetry={"anomaly_detected": True, "status": "ANOMALOUS", "confidence": 0.82, "severity": "HIGH"},
        thermal={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.85, "severity": "LOW"},
        wavelet={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.80, "severity": "LOW"},
        orbital={"collision_risk": True, "status": "CRITICAL", "risk_level": "CRITICAL", "confidence": 0.95},
        space_weather={"environmental_anomaly": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
    )
    ok = check(
        "TEST 5 — Orbital Critical + Telemetry Anomaly",
        result,
        {
            "anomaly_count": 2,
            "risk_level": "CRITICAL",
            "overall_severity": "CRITICAL",
        }
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # TEST 6 — Space weather alone → isolated environmental
    # --------------------------------------------------
    result = fusion.fuse(
        telemetry={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
        thermal={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.85, "severity": "LOW"},
        wavelet={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.80, "severity": "LOW"},
        orbital={"collision_risk": False, "status": "NOMINAL", "risk_level": "LOW", "confidence": 0.95},
        space_weather={"environmental_anomaly": True, "status": "ENVIRONMENTAL_ANOMALY", "confidence": 0.90, "severity": "MEDIUM"},
    )
    ok = check(
        "TEST 6 — Space Weather Alone",
        result,
        {
            "anomaly_count": 1,
            "primary_problem": "Elevated space-weather disturbance (isolated environmental anomaly)",
            "overall_severity": "MEDIUM",
        }
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # TEST 7 — Missing modality (None) → ANALYSIS_UNAVAILABLE, NOT normal
    # --------------------------------------------------
    result = fusion.fuse(
        telemetry={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
        thermal=None,  # missing
        wavelet=None,  # missing
        orbital=None,  # missing
        space_weather=None,  # missing
    )
    ok = check(
        "TEST 7 — Missing Modalities Not Counted As Normal",
        result,
        {
            "available_modalities": lambda v: v == ["telemetry"],
            "unavailable_modalities": lambda v: set(v) == {"thermal", "wavelet", "orbital", "space_weather"},
            "anomaly_count": 0,
            "normal_modalities": ["telemetry"],
        }
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # TEST 8 — Confidence increases with more corroborating anomalies
    # --------------------------------------------------
    result_single = fusion.fuse(
        telemetry={"anomaly_detected": True, "confidence": 0.80, "severity": "HIGH"},
        thermal=None,
        wavelet=None,
        orbital=None,
        space_weather=None,
    )
    result_triple = fusion.fuse(
        telemetry={"anomaly_detected": True, "confidence": 0.85, "severity": "HIGH"},
        thermal={"anomaly_detected": True, "confidence": 0.88, "severity": "HIGH"},
        wavelet={"anomaly_detected": True, "confidence": 0.82, "severity": "HIGH"},
        orbital=None,
        space_weather=None,
    )
    conf_ok = result_triple["confidence"] > result_single["confidence"]
    ok = check(
        "TEST 8 — Confidence Higher With More Corroborating Anomalies",
        {"conf_ok": conf_ok},
        {"conf_ok": True}
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # TEST 9 — Orbital WARNING alone
    # --------------------------------------------------
    result = fusion.fuse(
        telemetry={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
        thermal={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.85, "severity": "LOW"},
        wavelet={"anomaly_detected": False, "status": "NOMINAL", "confidence": 0.80, "severity": "LOW"},
        orbital={"collision_risk": False, "status": "WARNING", "risk_level": "HIGH", "confidence": 0.95},
        space_weather={"environmental_anomaly": False, "status": "NOMINAL", "confidence": 0.90, "severity": "LOW"},
    )
    ok = check(
        "TEST 9 — Orbital Warning Alone",
        result,
        {
            "anomaly_count": 1,
            "primary_problem": "Orbital close-approach warning",
            "overall_severity": "MEDIUM",
        }
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # TEST 10 — No modalities provided → low confidence
    # --------------------------------------------------
    result = fusion.fuse(
        telemetry=None,
        thermal=None,
        wavelet=None,
        orbital=None,
        space_weather=None,
    )
    ok = check(
        "TEST 10 - No Modalities - Low Confidence",
        result,
        {
            "available_modalities": [],
            "unavailable_modalities": lambda v: len(v) == 5,
            "anomaly_count": 0,
            "confidence": lambda v: v < 0.30,
        }
    )
    passed += int(ok); failed += int(not ok)

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    print('='*50)
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)

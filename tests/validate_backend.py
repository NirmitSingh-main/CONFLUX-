import sys
sys.path.insert(0, r"C:\Users\HP\Desktop\CONFLUX")

from backend.models.orbital import OrbitalState, Vector3D
from backend.physics.conjunction import assess_conjunction
from backend.intelligence.orbital_risk import OrbitalRiskAnalyzer
from datetime import datetime

risk_analyzer = OrbitalRiskAnalyzer()

# Test: Safe separation orbit
state1 = OrbitalState(
    object_id="SC-PRIMARY-01",
    timestamp=datetime.utcnow(),
    position=Vector3D(x=6871.0, y=0.0, z=0.0),
    velocity=Vector3D(x=0.0, y=7.61, z=0.0),
)
state2 = OrbitalState(
    object_id="DEBRIS-DELTA-44",
    timestamp=datetime.utcnow(),
    position=Vector3D(x=6950.0, y=45.0, z=32.0),
    velocity=Vector3D(x=-0.2, y=7.45, z=0.4),
)
conj = assess_conjunction(state1, state2, safety_distance=5.0)
result = risk_analyzer.analyze(conj)
print("SAFE ORBIT: status=" + result["status"] + " miss_distance=" + str(round(conj.miss_distance, 3)) + " km")
assert result["status"] == "NOMINAL", "Expected NOMINAL for safe orbit"

# Test: Critical close conjunction
state2_close = OrbitalState(
    object_id="DEBRIS-COSMOS-2251",
    timestamp=datetime.utcnow(),
    position=Vector3D(x=6871.3, y=0.2, z=0.1),
    velocity=Vector3D(x=0.05, y=7.60, z=0.02),
)
conj2 = assess_conjunction(state1, state2_close, safety_distance=5.0)
result2 = risk_analyzer.analyze(conj2)
print("CRITICAL: status=" + result2["status"] + " miss_distance=" + str(round(conj2.miss_distance, 3)) + " km collision_risk=" + str(conj2.collision_risk))
assert result2["status"] == "CRITICAL", "Expected CRITICAL for close conjunction"
assert conj2.collision_risk is True, "Expected collision_risk=True"

# Consistency: no contradictions
assert result["status"] == "NOMINAL" and conj.miss_distance > 5.0
assert result2["status"] == "CRITICAL" and conj2.miss_distance <= 5.0

print()
print("Space Weather thresholds test:")
from backend.intelligence.space_weather import SpaceWeatherAnalyzer
sw = SpaceWeatherAnalyzer(solar_activity_threshold=492.545, radiation_threshold=7.749, geomagnetic_activity_threshold=3.565)

# Quiet
r = sw.analyze(18.0, 0.8, 1.5)
assert not r["environmental_anomaly"], "Expected no anomaly for quiet conditions"
assert len(r["active_events"]) == 0, "Expected no events for quiet"
# Verify no duplicate events
assert len(r["active_events"]) == len(set(r["active_events"])), "Duplicate events detected!"
print("Quiet: environmental_anomaly=" + str(r["environmental_anomaly"]) + " active_events=" + str(r["active_events"]))

# All three elevated  
r2 = sw.analyze(600.0, 10.0, 5.0)
assert r2["environmental_anomaly"], "Expected anomaly for elevated conditions"
assert len(r2["active_events"]) == 3, "Expected 3 events"
assert len(r2["active_events"]) == len(set(r2["active_events"])), "Duplicate events detected!"
print("Elevated: active_events=" + str(r2["active_events"]))

print()
print("ALL VALIDATION CHECKS PASSED")

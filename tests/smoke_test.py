"""
CONFLUX Integration Smoke Test
Tests: CORS headers, all getLatest endpoints, telemetry POST, fusion POST
Run: .venv\Scripts\python tests\smoke_test.py
"""
import urllib.request
import urllib.error
import json
import sys
import os

# Fix Windows console encoding
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000"
ORIGIN = "http://localhost:3001"

def req(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode("utf-8") if body else None
    headers = {"Origin": ORIGIN, "Content-Type": "application/json"}
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, dict(resp.headers), json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), {}

def header(headers, name):
    name = name.lower()
    return next((value for key, value in headers.items() if key.lower() == name), "")

results = []

def test(name, ok, detail=""):
    sym = "PASS" if ok else "FAIL"
    suffix = f" [{detail}]" if detail else ""
    print(f"  [{sym}] {name}{suffix}")
    results.append(ok)

print()
print("=== CONFLUX Smoke Tests ===========================")
print(f"  Backend : {BASE}")
print(f"  Origin  : {ORIGIN}")
print()

# T1: Health
status, hdrs, body = req("GET", "/health")
test("GET /health -> 200", status == 200, f"HTTP {status}")

# T2: CORS header
cors = header(hdrs, "Access-Control-Allow-Origin")
test("CORS Allow-Origin header present", cors != "", f"'{cors}'")
test("CORS is explicit origin, not wildcard *", cors != "*", "CORS bug fixed")

# T3: Missions
status, _, body = req("GET", "/mission/")
test("GET /mission/ -> 200 or 404", status in [200, 404], f"HTTP {status}")
missions = body if isinstance(body, list) else body.get("missions", [])
if not missions and isinstance(body, dict):
    missions = body.get("data", [])
mission_id = missions[0]["id"] if missions else 1
print(f"    Missions in DB: {len(missions)}, using mission_id={mission_id}")

# T4: All getLatest/* endpoints (200=has data, 404=not analyzed, 422=ok)
for label, path in [
    ("Telemetry",     f"/telemetry/latest/{mission_id}"),
    ("Thermal",       f"/thermal/latest/{mission_id}"),
    ("Wavefront",     f"/wavefront/latest/{mission_id}"),
    ("Orbital",       f"/orbital/latest/{mission_id}"),
    ("Space Weather", f"/space-weather/latest/{mission_id}"),
    ("Fusion",        f"/fusion/latest/{mission_id}"),
]:
    status, _, _ = req("GET", path)
    test(f"GET {path}", status in [200, 404], f"HTTP {status}")

# T5: POST telemetry
status, hdrs2, body = req("POST", "/telemetry/", {
    "mission_id": mission_id,
    "temperature": 24.5, "voltage": 28.2, "current": 4.1,
    "battery": 95.0, "pressure": 101.3, "vibration": 0.05,
})
test("POST /telemetry/ -> 200", status == 200, f"HTTP {status}")
if status == 200:
    test("  telemetry.anomaly_detected field present", "anomaly_detected" in body)
    test("  CORS header on POST response", header(hdrs2, "Access-Control-Allow-Origin") != "")

# T6: POST space-weather
status, _, body = req("POST", "/space-weather/", {
    "mission_id": mission_id,
    "solar_activity": 25.0, "radiation_level": 1.2, "geomagnetic_activity": 2.0,
})
test("POST /space-weather/ -> 200", status == 200, f"HTTP {status}")

# T7: POST wavefront
status, _, body = req("POST", "/wavefront/", {
    "mission_id": mission_id,
    "wavefront_rms_um": 0.045, "tip_error_um": 0.012, "tilt_error_um": 0.015,
    "defocus_um": 0.020, "astigmatism_um": 0.018, "coma_um": 0.009,
})
test("POST /wavefront/ -> 200", status == 200, f"HTTP {status}")

# T8: POST orbital
status, _, body = req("POST", "/orbital/", {
    "mission_id": mission_id,
    "object1": {
        "object_id": "SC-PRIMARY-01", "timestamp": "2025-01-01T00:00:00Z",
        "position": {"x": 6871.0, "y": 0.0, "z": 0.0},
        "velocity": {"x": 0.0, "y": 7.61, "z": 0.0},
    },
    "object2": {
        "object_id": "DEBRIS-01", "timestamp": "2025-01-01T00:00:00Z",
        "position": {"x": 6950.0, "y": 45.0, "z": 32.0},
        "velocity": {"x": -0.2, "y": 7.45, "z": 0.4},
    },
    "safety_distance": 5.0,
})
test("POST /orbital/ -> 200", status == 200, f"HTTP {status}")

# T9: POST fusion (uses "wavefront" key, not "wavelet")
status, _, body = req("POST", "/fusion/", {
    "mission_id": mission_id,
    "modalities": ["telemetry", "space_weather", "orbital", "thermal", "wavefront"],
})
test("POST /fusion/ -> 200", status == 200, f"HTTP {status}")
if status == 200:
    test("  fusion.overall_severity present", "overall_severity" in body)
    test("  fusion.modality_states present", "modality_states" in body)
    test("  fusion uses 'wavefront' key (not 'wavelet')", "wavefront" in str(body))

# T10: Second getLatest now returns data (after POSTs)
status, _, body = req("GET", f"/telemetry/latest/{mission_id}")
test("GET /telemetry/latest/{id} -> 200 (after POST)", status == 200, f"HTTP {status}")

status, _, body = req("GET", f"/fusion/latest/{mission_id}")
test("GET /fusion/latest/{id} -> 200 (after POST)", status == 200, f"HTTP {status}")

# Summary
total = len(results)
passed = sum(results)
failed = total - passed
print()
print(f"=== Results: {passed}/{total} passed", end="")
if failed:
    print(f"  ({failed} FAILED) ===")
    sys.exit(1)
else:
    print(" -- ALL PASS ===")
    sys.exit(0)

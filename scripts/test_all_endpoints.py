import io
import json
import urllib.request
import urllib.parse
import numpy as np
import cv2

BASE_URL = "http://127.0.0.1:8000"


def test_get(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, f"GET {endpoint} failed with status {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        print(f"[OK] GET {endpoint} -> Success: {data}")

        return data


def test_post_json(endpoint: str, payload: dict):
    url = f"{BASE_URL}{endpoint}"
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, f"POST {endpoint} failed with status {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        print(f"[OK] POST {endpoint} -> Success (modality={data.get('modality', 'N/A')}, id={data.get('id', 'N/A')})")
        return data


def test_post_image(endpoint: str, mission_id: int):
    url = f"{BASE_URL}{endpoint}"
    
    # Create test 64x64 synthetic thermal image with a hotspot
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    img[10:20, 10:20] = [255, 255, 255] # Hotspot
    _, encoded_img = cv2.imencode(".png", img)
    img_bytes = encoded_img.tobytes()

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = bytearray()
    
    # Field: mission_id
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="mission_id"\r\n\r\n'.encode("utf-8"))
    body.extend(f"{mission_id}\r\n".encode("utf-8"))

    # Field: file
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="test_thermal.png"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: image/png\r\n\r\n")
    body.extend(img_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, f"POST {endpoint} failed with status {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        print(f"[OK] POST {endpoint} (multipart) -> Hotspot detected={data.get('anomaly_detected')}, ratio={data.get('hotspot_ratio')}")
        return data



def main():
    print("========================================")
    print("Testing CONFLUX FastAPI Endpoints...")
    print("========================================")

    # 1. System & Health
    test_get("/")
    test_get("/health")

    # 2. Missions
    missions = test_get("/missions/")
    mission_res = test_post_json(
        "/missions/",
        {
            "mission_name": "TEST-CYGNUS-9",
            "spacecraft_name": "CYGNUS-X1",
            "status": "ACTIVE",
        },
    )
    mission_id = mission_res["id"]
    test_get(f"/missions/{mission_id}")

    # 3. Telemetry Anomaly Evaluation
    test_post_json(
        "/telemetry/",
        {
            "mission_id": mission_id,
            "temperature": 75.2,
            "voltage": 32.4,
            "current": 12.8,
            "battery": 65.0,
            "pressure": 105.0,
            "vibration": 0.85,
        },
    )

    # 4. Imagery / Thermal Analysis
    test_post_image("/imagery/", mission_id)
    test_post_image("/thermal/", mission_id)

    # 5. Optical Wavefront Evaluation
    test_post_json(
        "/wavefront/",
        {
            "mission_id": mission_id,
            "wavefront_rms_um": 0.25,
            "tip_error_um": 0.12,
            "tilt_error_um": 0.15,
            "defocus_um": 0.08,
            "astigmatism_um": 0.22,
            "coma_um": 0.29,
        },
    )

    # 6. Orbital Conjunction Assessment
    test_post_json(
        "/orbital/",
        {
            "mission_id": mission_id,
            "object1": {
                "object_id": "CYGNUS-X1",
                "timestamp": "2026-08-31T20:00:00Z",
                "position": {"x": 6871.0, "y": 0.0, "z": 0.0},
                "velocity": {"x": 0.0, "y": 7.61, "z": 0.0},
            },
            "object2": {
                "object_id": "DEBRIS-TEST",
                "timestamp": "2026-08-31T20:00:00Z",
                "position": {"x": 6871.3, "y": 0.2, "z": 0.1},
                "velocity": {"x": 0.05, "y": 7.60, "z": 0.02},
            },
            "safety_distance": 5.0,
        },
    )

    # 7. Space Weather Evaluation
    test_post_json(
        "/space-weather/",
        {
            "mission_id": mission_id,
            "solar_activity": 180.0,
            "radiation_level": 15.5,
            "geomagnetic_activity": 4.5,
        },
    )
    test_post_json(
        "/weather/",
        {
            "mission_id": mission_id,
            "solar_activity": 22.0,
            "radiation_level": 1.2,
            "geomagnetic_activity": 1.8,
        },
    )

    # 8. Multimodal Fusion Synthesis
    test_post_json(
        "/fusion/",
        {
            "mission_id": mission_id,
            "telemetry": {"anomaly_detected": True},
            "thermal": {"anomaly_detected": True},
            "wavelet": {"anomaly_detected": True},
            "orbital": {"status": "CRITICAL"},
            "space_weather": {"environmental_anomaly": True},
        },
    )

    # 9. Mission History & Queries
    test_get(f"/missions/{mission_id}/observations")
    test_get(f"/missions/{mission_id}/anomalies")
    test_get(f"/missions/{mission_id}/fusion")

    print("========================================")
    print("ALL API ENDPOINTS TESTED AND PASSED!")
    print("========================================")


if __name__ == "__main__":
    main()

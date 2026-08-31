"""
Mission Isolation Tests for CONFLUX
Verifies that all /latest/{mission_id} endpoints correctly filter by mission_id
and that Mission #2 data never bleeds into Mission #1 results.
"""

import sys
from pathlib import Path

# Ensure the workspace root is on the path so backend imports work from any CWD
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import the app first — this triggers all router imports which in turn
# register every SQLAlchemy model class with Base.metadata
from backend.main import app  # noqa: E402 (app import must happen before create_all)
from backend.database.database import Base, get_db
from backend.database.models import (  # noqa: F401
    Mission,
    Observation,
    AnomalyEvent,
    OrbitalAnalysis,
    SpaceWeatherAnalysis,
    TelemetryAnalysis,
    ThermalAnalysis,
    WavefrontAnalysis,
    FusionAnalysis,
    FusionEvent,
)


# ---------------------------------------------------------------------------
# In-memory SQLite database fixture — isolated per test session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def in_memory_db():
    """Create an in-memory SQLite engine and populate it with Mission #1 data only.

    SQLite `:memory:` databases are per-connection — use StaticPool so all
    sessions (fixture setup + request handlers) share the exact same connection.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    session = TestSession()

    # Seed Mission #1
    mission1 = Mission(
        id=1,
        mission_name="ARES-V DEEP RECON",
        spacecraft_name="ORION-X4",
        status="ACTIVE",
    )
    session.add(mission1)

    # Seed one telemetry analysis for Mission #1 only
    telemetry_m1 = TelemetryAnalysis(
        mission_id=1,
        temperature=22.5,
        voltage=28.1,
        current=3.4,
        battery=87.0,
        pressure=1.01,
        vibration=0.02,
        anomaly_detected=False,
        model_output=1,
        decision_value=0.15,
        severity="LOW",
        confidence=0.92,
        status="NOMINAL",
    )
    session.add(telemetry_m1)
    session.commit()
    session.close()

    yield engine, TestSession

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(in_memory_db):
    """Build a TestClient that overrides get_db to use the in-memory database."""
    _, TestSession = in_memory_db

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 1 — Mission #2 returns 404 when only Mission #1 has telemetry data
# ---------------------------------------------------------------------------

def test_mission2_telemetry_404_when_only_mission1_has_data(client):
    """
    GET /telemetry/latest/2 must return 404 when the database only contains
    telemetry records for mission_id=1.  Mission #2 data must not be served.
    """
    response = client.get("/telemetry/latest/2")
    assert response.status_code == 404, (
        f"Expected 404 for mission 2 (no data), got {response.status_code}: {response.text}"
    )
    detail = response.json().get("detail", "")
    assert "2" in detail, f"Error detail should reference mission 2, got: {detail}"


# ---------------------------------------------------------------------------
# Test 2 — Mission #1 telemetry data is still reachable and correct
# ---------------------------------------------------------------------------

def test_mission1_telemetry_returns_correct_data(client):
    """
    GET /telemetry/latest/1 must return the seeded Mission #1 record.
    """
    response = client.get("/telemetry/latest/1")
    assert response.status_code == 200, (
        f"Expected 200 for mission 1, got {response.status_code}: {response.text}"
    )
    data = response.json()
    assert data["mission_id"] == 1
    assert data["status"] == "NOMINAL"
    assert data["anomaly_detected"] is False


# ---------------------------------------------------------------------------
# Test 3 — Mission #1 data is unaffected after a Mission #2 operation
# ---------------------------------------------------------------------------

def test_mission1_unaffected_by_mission2_operation(client, in_memory_db):
    """
    After inserting a telemetry record for Mission #2, the GET /telemetry/latest/1
    endpoint must still return Mission #1's own data, never Mission #2's.
    """
    _, TestSession = in_memory_db
    session = TestSession()

    # Insert an anomalous telemetry record for mission_id=2
    telemetry_m2 = TelemetryAnalysis(
        mission_id=2,
        temperature=95.0,   # very hot — anomalous
        voltage=14.0,
        current=12.0,
        battery=10.0,
        pressure=3.5,
        vibration=2.8,
        anomaly_detected=True,
        model_output=-1,
        decision_value=-0.45,
        severity="HIGH",
        confidence=0.97,
        status="ANOMALOUS",
    )
    session.add(telemetry_m2)
    session.commit()
    session.close()

    # Mission #1 must still return its own NOMINAL record
    response1 = client.get("/telemetry/latest/1")
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["mission_id"] == 1, "mission_id must be 1"
    assert data1["status"] == "NOMINAL", "Mission #1 status must remain NOMINAL"
    assert data1["anomaly_detected"] is False, "Mission #1 must not show Mission #2 anomaly"

    # Mission #2 must now return its own ANOMALOUS record
    response2 = client.get("/telemetry/latest/2")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["mission_id"] == 2, "mission_id must be 2"
    assert data2["status"] == "ANOMALOUS", "Mission #2 must return its own ANOMALOUS status"
    assert data2["anomaly_detected"] is True


def test_fusion_accepts_wavefront_modality_alias(client, in_memory_db):
    """Fusion must accept the canonical wavefront key and keep results mission-scoped."""
    _, TestSession = in_memory_db
    session = TestSession()

    session.add(
        WavefrontAnalysis(
            mission_id=1,
            wavefront_rms_um=0.045,
            tip_error_um=0.012,
            tilt_error_um=0.015,
            defocus_um=0.02,
            astigmatism_um=0.018,
            coma_um=0.009,
            anomaly_detected=False,
            anomaly_score=0.7,
            max_z_score=0.8,
            energy_ratio=1.1,
            wavelet_anomaly=False,
            severity="LOW",
            confidence=0.8,
            status="NOMINAL",
        )
    )
    session.commit()
    session.close()

    response = client.post(
        "/fusion/",
        json={"mission_id": 1, "modalities": ["wavefront"]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "wavefront" in payload["available_modalities"]
    assert "wavefront" in payload["modality_states"]

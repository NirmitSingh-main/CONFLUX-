from fastapi.testclient import TestClient

from backend.main import app
from backend.rag.assistant import compose_guidance
from backend.rag.retriever import retrieve


client = TestClient(app)


def test_rag_requires_fusion_result():
    response = client.post("/rag/", json={"mission_id": 1})
    assert response.status_code == 200
    assert response.json()["retrieval_status"] == "RUN_MULTIMODAL_FUSION_FIRST"


def test_rag_returns_relevant_grounded_evidence():
    fusion = {
        "mission_id": 1,
        "primary_problem": "Potential environmental-driven subsystem anomaly cascade",
        "overall_severity": "HIGH",
        "risk_level": "HIGH",
        "modality_states": {
            "space_weather": {"status": "ANOMALOUS", "severity": "HIGH"},
            "telemetry": {"status": "ANOMALOUS", "severity": "HIGH"},
            "thermal": {"status": "ANOMALOUS", "severity": "HIGH"},
        },
    }
    response = client.post("/rag/", json={"mission_id": 1, "fusion_result": fusion})
    assert response.status_code == 200
    body = response.json()
    assert body["mission_id"] == 1
    assert body["retrieval_status"] == "EVIDENCE_RETRIEVED"
    assert body["evidence"]
    assert body["sources"]
    assert all(item["source"].startswith("knowledge/") for item in body["evidence"])
    assert all(item["relevance_score"] >= 0.20 for item in body["evidence"])
    assert all(not item["excerpt"].lstrip().startswith("#") for item in body["evidence"])
    assert "retrieved development/demo material states" in body["technical_interpretation"]


def test_rag_filters_low_score_documents():
    evidence = retrieve("thermal telemetry anomaly", limit=10)
    assert evidence
    assert all(item["relevance_score"] >= 0.20 for item in evidence)
    assert not any(item["source"].endswith("DEMO_conjunction_response.md") for item in evidence)


def test_rag_reports_no_relevant_knowledge():
    fusion = {
        "mission_id": 1,
        "primary_problem": "Unrelated lunar communications failure",
        "overall_severity": "LOW",
        "risk_level": "LOW",
    }
    response = client.post("/rag/", json={"mission_id": 1, "fusion_result": fusion})
    assert response.status_code == 200
    assert response.json()["retrieval_status"] == "NO_RELEVANT_KNOWLEDGE_FOUND"


def test_rag_reports_insufficient_evidence():
    result = compose_guidance(
        [{"source": "knowledge/demo.md", "relevance_score": 0.04, "excerpt": "A weak match."}],
        {"primary_problem": "test"},
    )
    assert result["retrieval_status"] == "INSUFFICIENT_KNOWLEDGE_BASE_EVIDENCE"
    assert result["technical_interpretation"] == "INSUFFICIENT KNOWLEDGE BASE EVIDENCE"


def test_rag_guidance_is_grounded_and_deduplicated():
    result = compose_guidance(
        [{
            "source": "knowledge/demo.md",
            "title": "DEMO Thermal Telemetry",
            "document_type": "md",
            "relevance_score": 0.8,
            "excerpt": "Operational guidance: inspect the thermal frame and sensor channels together, monitor the affected subsystem for persistence.",
        }],
        {"primary_problem": "thermal and telemetry anomaly"},
    )
    assert result["retrieval_status"] == "EVIDENCE_RETRIEVED"
    assert result["recommendations"] == [
        "inspect the thermal frame",
        "sensor channels together",
        "monitor the affected subsystem for persistence",
    ]
    assert "thermal frame" in result["technical_interpretation"]


def test_rag_is_mission_scoped():
    response = client.post("/rag/", json={"mission_id": 999999, "fusion_result": {"primary_problem": "thermal anomaly"}})
    assert response.status_code == 404

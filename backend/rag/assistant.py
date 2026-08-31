from typing import Any
import re


def build_query(fusion: dict[str, Any]) -> str:
    states = fusion.get("modality_states") or {}
    state_terms = []
    for name, state in states.items():
        if isinstance(state, dict):
            state_terms.extend([name, str(state.get("status", "")), str(state.get("severity", ""))])
    state_terms.extend([
        str(fusion.get("primary_problem", "")),
        str(fusion.get("overall_severity", "")),
        str(fusion.get("risk_level", "")),
    ])
    return " ".join(term for term in state_terms if term and term.lower() != "none")


def compose_guidance(evidence: list[dict], fusion: dict[str, Any]) -> dict[str, Any]:
    if not evidence:
        return {
            "retrieval_status": "NO_RELEVANT_KNOWLEDGE_FOUND",
            "technical_interpretation": "NO RELEVANT KNOWLEDGE FOUND",
            "recommendations": [],
            "sources": [],
            "source_entries": [],
        }

    if max(item["relevance_score"] for item in evidence) < 0.20:
        return {
            "retrieval_status": "INSUFFICIENT_KNOWLEDGE_BASE_EVIDENCE",
            "technical_interpretation": "INSUFFICIENT KNOWLEDGE BASE EVIDENCE",
            "recommendations": [],
            "sources": [item["source"] for item in evidence],
            "source_entries": [
                {"title": item.get("title", item["source"]), "source": item["source"], "document_type": item.get("document_type", "unknown")}
                for item in evidence
            ],
        }

    excerpts = " ".join(item["excerpt"] for item in evidence)
    recommendations = []
    for item in evidence:
        for sentence in item["excerpt"].split("."):
            sentence = sentence.strip()
            if "operational guidance:" in sentence.lower():
                guidance = sentence.split(":", 1)[1].strip()
                for action in re.split(r",\s*|\s+and\s+", guidance):
                    action = action.strip()
                    if action and action not in recommendations:
                        recommendations.append(action.rstrip("."))

    return {
        "retrieval_status": "EVIDENCE_RETRIEVED",
        "technical_interpretation": (
            "The retrieved development/demo material states: "
            f"{excerpts[:600]} "
            "This is retrieved technical context, not an observed spacecraft measurement."
        ),
        "recommendations": recommendations[:4],
        "sources": sorted({item["source"] for item in evidence}),
        "source_entries": [
            {"title": item.get("title", item["source"]), "source": item["source"], "document_type": item.get("document_type", "unknown")}
            for item in evidence
        ],
    }

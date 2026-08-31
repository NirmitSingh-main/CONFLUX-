from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import Mission
from backend.rag.assistant import build_query, compose_guidance
from backend.rag.retriever import retrieve

router = APIRouter()


class RagRequest(BaseModel):
    mission_id: int
    fusion_result: dict[str, Any] | None = None
    fusion_context: dict[str, Any] | None = Field(default=None)


@router.post("/")
def retrieve_mission_guidance(request: RagRequest, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == request.mission_id).first()
    if mission is None:
        raise HTTPException(status_code=404, detail=f"Mission {request.mission_id} not found.")

    fusion = request.fusion_result or request.fusion_context
    if not fusion:
        return {
            "mission_id": request.mission_id,
            "retrieval_status": "RUN_MULTIMODAL_FUSION_FIRST",
            "query": "",
            "evidence": [],
            "sources": [],
            "technical_interpretation": "RUN MULTIMODAL FUSION FIRST",
            "recommendations": [],
            "source_entries": [],
        }

    query = build_query(fusion)
    evidence = retrieve(query)
    guidance = compose_guidance(evidence, fusion)
    return {
        "mission_id": request.mission_id,
        "query": query,
        "evidence": evidence,
        **guidance,
    }

from datetime import datetime

from pydantic import BaseModel, Field


class Decision(BaseModel):
    decision_id: str
    timestamp: datetime

    action: str
    reason: str

    risk_score: float = Field(
        ge=0,
        le=1,
        description="Estimated risk associated with the current mission condition"
    )

    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence in the proposed decision"
    )

    expected_benefit: float = Field(
        ge=0,
        le=1,
        description="Estimated benefit of taking the proposed action"
    )

    safety_validated: bool = False
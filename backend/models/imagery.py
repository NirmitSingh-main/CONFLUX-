from datetime import datetime

from pydantic import BaseModel, Field


class ImageryObservation(BaseModel):
    timestamp: datetime
    image_path: str
    sensor: str = "infrared"

    min_temperature: float | None = None
    max_temperature: float | None = None
    mean_temperature: float | None = None

    anomaly_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Probability of a thermal anomaly"
    )
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
        description="Normalized confidence that a thermal anomaly is present",
    )

    hotspot_detected: bool = False

    hotspot_ratio: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Fraction of image pixels identified as thermal hotspots",
    )

    hottest_x: int | None = None
    hottest_y: int | None = None

    processing_method: str = "statistical"
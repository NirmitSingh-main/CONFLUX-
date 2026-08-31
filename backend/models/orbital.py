from datetime import datetime

from pydantic import BaseModel, Field


class Vector3D(BaseModel):
    x: float
    y: float
    z: float


class OrbitalState(BaseModel):
    object_id: str
    timestamp: datetime

    position: Vector3D = Field(
        description="Position vector in kilometers",
    )

    velocity: Vector3D = Field(
        description="Velocity vector in kilometers per second",
    )

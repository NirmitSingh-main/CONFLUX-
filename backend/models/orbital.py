from datetime import datetime

from pydantic import BaseModel


class Vector3D(BaseModel):
    x: float
    y: float
    z: float


class OrbitalState(BaseModel):
    object_id: str
    timestamp: datetime
    position: Vector3D
    velocity: Vector3D
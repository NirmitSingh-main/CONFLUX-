from datetime import datetime

from pydantic import BaseModel, Field


class TelemetryReading(BaseModel):
    timestamp: datetime

    temperature: float = Field(
        ...,
        description="Spacecraft temperature in Celsius",
    )

    voltage: float = Field(
        ...,
        description="Spacecraft voltage in volts",
    )

    current: float = Field(
        ...,
        description="Spacecraft current in amperes",
    )

    battery: float = Field(
        ...,
        ge=0,
        le=100,
        description="Battery level in percent",
    )

    pressure: float = Field(
        ...,
        description="Spacecraft pressure",
    )

    vibration: float = Field(
        ...,
        ge=0,
        description="Vibration measurement",
    )

    radiation: float = Field(
        default=0.0,
        ge=0,
        description="Radiation measurement or exposure indicator",
    )

    signal_strength: float | None = Field(
        default=None,
        description="Communication signal strength",
    )
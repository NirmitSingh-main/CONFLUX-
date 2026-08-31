from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


# --------------------------------------------------
# Core mission table
# --------------------------------------------------

class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_name: Mapped[str] = mapped_column(String(200), nullable=False)
    spacecraft_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --------------------------------------------------
# Legacy generic observation / anomaly tables
# (kept for backward compat)
# --------------------------------------------------

class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)
    modality: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    event: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)
    modality: Mapped[str] = mapped_column(String(50), nullable=False)
    anomaly_type: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --------------------------------------------------
# Structured per-modality analysis tables
# --------------------------------------------------

class OrbitalAnalysis(Base):
    __tablename__ = "orbital_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)

    object1_id: Mapped[str] = mapped_column(String(200), nullable=False)
    object2_id: Mapped[str] = mapped_column(String(200), nullable=False)

    # Input vectors (stored for audit trail)
    primary_position_x: Mapped[float] = mapped_column(Float, nullable=False)
    primary_position_y: Mapped[float] = mapped_column(Float, nullable=False)
    primary_position_z: Mapped[float] = mapped_column(Float, nullable=False)
    primary_velocity_x: Mapped[float] = mapped_column(Float, nullable=False)
    primary_velocity_y: Mapped[float] = mapped_column(Float, nullable=False)
    primary_velocity_z: Mapped[float] = mapped_column(Float, nullable=False)
    secondary_position_x: Mapped[float] = mapped_column(Float, nullable=False)
    secondary_position_y: Mapped[float] = mapped_column(Float, nullable=False)
    secondary_position_z: Mapped[float] = mapped_column(Float, nullable=False)
    secondary_velocity_x: Mapped[float] = mapped_column(Float, nullable=False)
    secondary_velocity_y: Mapped[float] = mapped_column(Float, nullable=False)
    secondary_velocity_z: Mapped[float] = mapped_column(Float, nullable=False)

    safety_threshold: Mapped[float] = mapped_column(Float, nullable=False)

    # Computed outputs
    current_distance: Mapped[float] = mapped_column(Float, nullable=False)
    miss_distance: Mapped[float] = mapped_column(Float, nullable=False)
    relative_speed: Mapped[float] = mapped_column(Float, nullable=False)
    time_to_closest_approach: Mapped[float] = mapped_column(Float, nullable=False)

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # NOMINAL / WARNING / CRITICAL
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)  # LOW / MEDIUM / HIGH / CRITICAL
    collision_risk: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SpaceWeatherAnalysis(Base):
    __tablename__ = "space_weather_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Input values
    solar_activity: Mapped[float] = mapped_column(Float, nullable=False)
    radiation_level: Mapped[float] = mapped_column(Float, nullable=False)
    geomagnetic_activity: Mapped[float] = mapped_column(Float, nullable=False)

    # Per-channel status flags
    solar_event: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    radiation_event: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    geomagnetic_event: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Derived status
    active_events: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list stored as string
    environmental_anomaly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    overall_status: Mapped[str] = mapped_column(String(50), nullable=False, default="NOMINAL")
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.90)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TelemetryAnalysis(Base):
    __tablename__ = "telemetry_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Input measurements
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    voltage: Mapped[float] = mapped_column(Float, nullable=False)
    current: Mapped[float] = mapped_column(Float, nullable=False)
    battery: Mapped[float] = mapped_column(Float, nullable=False)
    pressure: Mapped[float] = mapped_column(Float, nullable=False)
    vibration: Mapped[float] = mapped_column(Float, nullable=False)

    # Analysis outputs
    anomaly_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    model_output: Mapped[int | None] = mapped_column(Integer, nullable=True)
    decision_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.80)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="NOMINAL")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ThermalAnalysis(Base):
    __tablename__ = "thermal_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Image metadata
    filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mean_intensity: Mapped[float | None] = mapped_column(Float, nullable=True)
    standard_deviation: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    hottest_intensity: Mapped[float | None] = mapped_column(Float, nullable=True)
    hotspot_pixels: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hotspot_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Analysis outputs
    anomaly_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.80)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="NOMINAL")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WavefrontAnalysis(Base):
    __tablename__ = "wavefront_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Input optical measurements
    wavefront_rms_um: Mapped[float] = mapped_column(Float, nullable=False)
    tip_error_um: Mapped[float] = mapped_column(Float, nullable=False)
    tilt_error_um: Mapped[float] = mapped_column(Float, nullable=False)
    defocus_um: Mapped[float] = mapped_column(Float, nullable=False)
    astigmatism_um: Mapped[float] = mapped_column(Float, nullable=False)
    coma_um: Mapped[float] = mapped_column(Float, nullable=False)

    # Analysis outputs
    anomaly_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    anomaly_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_z_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    wavelet_anomaly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.80)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="NOMINAL")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FusionAnalysis(Base):
    __tablename__ = "fusion_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Which analyses were consumed
    orbital_analysis_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    space_weather_analysis_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    telemetry_analysis_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    thermal_analysis_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wavefront_analysis_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Modality state summary (comma-separated names)
    available_modalities: Mapped[str | None] = mapped_column(Text, nullable=True)
    anomalous_modalities: Mapped[str | None] = mapped_column(Text, nullable=True)
    normal_modalities: Mapped[str | None] = mapped_column(Text, nullable=True)
    unavailable_modalities: Mapped[str | None] = mapped_column(Text, nullable=True)

    anomaly_count: Mapped[int] = mapped_column(Integer, default=0)
    multi_modal_agreement: Mapped[bool] = mapped_column(Boolean, default=False)

    # Correlated analysis results
    correlated_events: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_problem: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_severity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --------------------------------------------------
# Legacy fusion event table (kept for backward compat)
# --------------------------------------------------

class FusionEvent(Base):
    __tablename__ = "fusion_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, nullable=False)
    anomaly_count: Mapped[int] = mapped_column(Integer, default=0)
    multi_modal_agreement: Mapped[bool] = mapped_column(default=False)
    anomalous_modalities: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

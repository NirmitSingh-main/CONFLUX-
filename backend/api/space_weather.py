from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import (
    Observation,
    AnomalyEvent,
)
from backend.intelligence.space_weather import (
    SpaceWeatherAnalyzer,
)


router = APIRouter()


# --------------------------------------------------
# Request model
# --------------------------------------------------

class SpaceWeatherInput(BaseModel):
    mission_id: int

    solar_activity: float
    radiation_level: float
    geomagnetic_activity: float


# --------------------------------------------------
# Analyzer
# --------------------------------------------------

analyzer = SpaceWeatherAnalyzer(
    solar_activity_threshold=492.545,
    radiation_threshold=7.749,
    geomagnetic_activity_threshold=3.565,
)


# --------------------------------------------------
# Space-weather analysis endpoint
# --------------------------------------------------

@router.post("/")
def analyze_space_weather(
    request: SpaceWeatherInput,
    db: Session = Depends(get_db),
):

    # Analyze the measured environmental conditions.

    result = analyzer.analyze(
        solar_activity=request.solar_activity,
        radiation_level=request.radiation_level,
        geomagnetic_activity=request.geomagnetic_activity,
    )

    # ------------------------------------------------
    # Store observation
    # ------------------------------------------------

    observation = Observation(
        mission_id=request.mission_id,
        modality="space_weather",
        value=request.radiation_level,
        event=(
            ", ".join(result["active_events"])
            if result["active_events"]
            else "NO_SIGNIFICANT_SPACE_WEATHER_EVENT"
        ),
    )

    db.add(observation)

    # ------------------------------------------------
    # Store anomaly
    # ------------------------------------------------

    if result["environmental_anomaly"]:

        anomaly = AnomalyEvent(
            mission_id=request.mission_id,
            modality="space_weather",
            anomaly_type=", ".join(
                result["active_events"]
            ),
            description=(
                "Elevated space-weather activity "
                "detected from environmental "
                "measurements."
            ),
        )

        db.add(anomaly)

    db.commit()

    # ------------------------------------------------
    # Return result
    # ------------------------------------------------

    return {
        "mission_id": request.mission_id,
        "modality": "space_weather",

        "solar_activity":
            result["solar_activity"],

        "radiation_level":
            result["radiation_level"],

        "geomagnetic_activity":
            result["geomagnetic_activity"],

        "solar_event":
            result["solar_event"],

        "radiation_event":
            result["radiation_event"],

        "geomagnetic_event":
            result["geomagnetic_event"],

        "active_events":
            result["active_events"],

        "environmental_anomaly":
            result["environmental_anomaly"],

        "stored_in_database": True,
    }
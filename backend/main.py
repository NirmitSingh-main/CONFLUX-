from fastapi import FastAPI
from backend.api.wavefront import router as wavefront_router
from backend.api.imagery import router as imagery_router
from backend.api.mission import router as mission_router
from backend.api.telemetry import router as telemetry_router
from backend.api.orbital import router as orbital_router

from backend.api.space_weather import (
    router as space_weather_router,
)
from backend.api.fusion import (
    router as fusion_router,
)

app = FastAPI(
    title="CONFLUX",
    description="Multimodal AI for Real-Time Space Mission Intelligence",
    version="1.0.0",
)
app.include_router(
    wavefront_router,
    prefix="/wavefront",
    tags=["Wavefront"],
)

app.include_router(
    imagery_router,
    prefix="/imagery",
    tags=["Imagery"],
)

app.include_router(
    space_weather_router,
    prefix="/space-weather",
    tags=["Space Weather"],
)

app.include_router(
    fusion_router,
    prefix="/fusion",
    tags=["Fusion"],
)
app.include_router(
    telemetry_router,
    prefix="/telemetry",
    tags=["Telemetry"],
)

app.include_router(
    mission_router,
    prefix="/missions",
    tags=["Missions"],
)

app.include_router(
    orbital_router,
    prefix="/orbital",
    tags=["Orbital"],
)


@app.get("/")
def root():
    return {
        "system": "CONFLUX",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
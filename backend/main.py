from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.database import engine, Base
import backend.database.models  # noqa: F401 — must import before create_all

from backend.api.wavefront import router as wavefront_router
from backend.api.imagery import router as imagery_router
from backend.api.mission import router as mission_router
from backend.api.telemetry import router as telemetry_router
from backend.api.orbital import router as orbital_router
from backend.api.space_weather import router as space_weather_router
from backend.api.fusion import router as fusion_router
from backend.api.rag import router as rag_router

# ─── Database ───────────────────────────────────────────────────────────────
# Create all tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

# ─── Application ────────────────────────────────────────────────────────────
app = FastAPI(
    title="CONFLUX",
    description="Multimodal AI for Real-Time Space Mission Intelligence",
    version="1.0.0",
)

# ─── CORS ────────────────────────────────────────────────────────────────────
# IMPORTANT: allow_origins=["*"] combined with allow_credentials=True is INVALID
# per the CORS spec. Browsers will reject ALL preflight requests with that
# combination ("Failed to fetch" / "Network error").
#
# Fix: use an explicit list of allowed origins (all local Vite dev ports) and
# set allow_credentials=False because the frontend sends no cookies or auth tokens.
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization", "X-Requested-With"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(wavefront_router, prefix="/wavefront", tags=["Wavefront"])
app.include_router(imagery_router,   prefix="/imagery",   tags=["Imagery"])
app.include_router(imagery_router,   prefix="/thermal",   tags=["Thermal"])   # alias
app.include_router(space_weather_router, prefix="/space-weather", tags=["Space Weather"])
app.include_router(space_weather_router, prefix="/weather",       tags=["Space Weather"])  # alias
app.include_router(fusion_router,    prefix="/fusion",    tags=["Fusion"])
app.include_router(rag_router,       prefix="/rag",       tags=["RAG"])
app.include_router(telemetry_router, prefix="/telemetry", tags=["Telemetry"])
app.include_router(mission_router,   prefix="/missions",  tags=["Missions"])
app.include_router(mission_router,   prefix="/mission",   tags=["Missions"])  # alias
app.include_router(orbital_router,   prefix="/orbital",   tags=["Orbital"])


# ─── Health ──────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"system": "CONFLUX", "status": "online"}


@app.get("/health")
def health():
    return {"status": "healthy"}

# 🛰️ CONFLUX

## Multimodal AI for Real-Time Space Mission Intelligence

CONFLUX is an AI-powered decision-support system designed to help detect, understand, and respond to complex situations during space missions.

Modern spacecraft generate large amounts of information from telemetry, infrared sensors, scientific instruments, orbital tracking systems, and space-weather observations. The challenge is that an important problem may not be visible in one data source alone. Small changes across several systems can combine into a much more serious mission condition.

CONFLUX brings these different sources together and uses AI, signal processing, and physics-based analysis to create a unified view of the spacecraft and its environment.

---

## 🤖 Built with IBM Bob

CONFLUX was developed with the assistance of **IBM Bob**, an AI software engineering agent. Bob played a central role throughout the project — from scaffolding the FastAPI backend and SQLAlchemy database models to designing the deterministic multimodal fusion engine that correlates anomalies across five independent sensing modalities. Bob helped architect the RAG (Retrieval-Augmented Generation) pipeline used to ingest mission knowledge documents and surface contextually relevant references during operator queries. It also assisted in training and evaluating the Isolation Forest telemetry anomaly detector, implementing the wavefront optical aberration classifier, and writing the physics-based orbital conjunction analysis using linear closest-approach geometry. On the frontend, Bob built the full React/TypeScript interface including the mission-scoped state management, the Aceternity 3D Globe integration, and the real-time fusion results page. End-to-end test suites covering mission isolation, fusion logic, and backend validation were also written with Bob's help.

---

# 🚀 How CONFLUX Works

## 📡 Spacecraft Telemetry

Telemetry provides continuous information about the condition of a spacecraft, such as temperature, voltage, current, battery state, pressure, vibration, and other subsystem measurements.

CONFLUX analyzes these measurements over time to detect unusual values and trends. Machine-learning and deep-learning models can identify patterns that differ from normal spacecraft behavior.

Instead of only asking whether a value has crossed a fixed threshold, CONFLUX can also consider how that value is changing over time.

---

## 🌡️ Infrared / Thermal Intelligence

Infrared imagery provides information about the thermal behavior of a spacecraft or its environment.

CONFLUX uses computer-vision techniques to analyze infrared images and identify unusual thermal patterns such as localized hotspots, abnormal temperature distributions, or changes between observations.

For example, an infrared image may show a developing hotspot while telemetry simultaneously reports increasing temperature and power consumption. These observations can be combined to provide stronger evidence of a possible subsystem problem.

```text
Infrared Image
      ↓
Thermal Pattern Detection
      ↓
Hotspot / Temperature Anomaly
      ↓
Combine with Telemetry
      ↓
Mission-Level Assessment
```

This makes infrared sensing more than just an image displayed on a dashboard. It becomes another source of physical evidence about the condition of the mission.

---

## 🔬 Wavefront and Wavelet-Based Sensor Analysis

CONFLUX also explores scientific sensor signals such as wavefront measurements.

A wavefront describes the shape and phase of an optical wave. Changes in the wavefront can contain information about disturbances, optical degradation, or changes in the observed system.

Raw sensor signals can be difficult to interpret because important events may occur at different time and frequency scales.

CONFLUX therefore uses wavelet analysis to break signals into different scales and identify localized changes.

```text
Wavefront Sensor
       ↓
Raw Signal
       ↓
Wavelet Decomposition
       ↓
Multi-Scale Features
       ↓
Anomaly Detection
       ↓
Wavefront Risk Signal
```

Wavelets are particularly useful for identifying transient events because they provide information about both when a change occurred and at what scale or frequency it occurred.

These wavelet-derived features can then be combined with telemetry and other sensor information.

---

## 🛰️ Orbital Intelligence

CONFLUX uses orbital data together with physics-based calculations to understand spacecraft motion and potential conjunction risks.

Orbital information can be propagated to estimate future position and velocity, while relative-motion calculations can be used to determine how spacecraft and other objects are moving with respect to each other.

```text
Orbital Data
     ↓
Orbit Propagation
     ↓
Position + Velocity
     ↓
Relative Motion
     ↓
Closest Approach
     ↓
Orbital Risk
```

This provides a physics-based source of information that can be combined with the AI-generated anomaly signals.

---

## ☀️ Space Weather

Spacecraft are also affected by their surrounding space environment.

CONFLUX can incorporate information about solar activity, radiation, geomagnetic conditions, and other space-weather events to understand how environmental changes may affect spacecraft operations.

For example, increased radiation conditions can become additional context when the spacecraft is already experiencing sensor or subsystem anomalies.

```text
Space Weather
      ↓
Environmental Conditions
      ↓
Spacecraft Exposure
      ↓
Mission Risk
```

---

# 🧠 Multimodal Fusion

The central idea of CONFLUX is to combine these different sources rather than treating every alert independently.

For example:

```text
Telemetry
→ Temperature increasing

Infrared
→ Localized hotspot detected

Wavelet Analysis
→ Abnormal sensor disturbance

Space Weather
→ Increased radiation

Orbital Physics
→ Changing orbital conditions
```

Individually, each observation may have limited meaning.

Together, they may provide evidence of a much more significant mission condition.

CONFLUX therefore uses a multimodal fusion layer to combine these observations and produce a higher-level assessment of the mission state.

---

# 🎯 Mission Intelligence

The system maintains an overall view of the mission condition and prioritizes important events.

Instead of presenting an operator with many unrelated alerts, CONFLUX attempts to answer:

- **What is happening?**
- **Which systems are affected?**
- **Are the detected anomalies related?**
- **How serious is the situation?**
- **What could happen next?**
- **What responses are available?**

---

# 🧪 Simulation and Response Analysis

When a significant event is detected, CONFLUX can use a lightweight digital-twin environment to explore possible outcomes.

Different responses can be simulated and compared before being presented to the operator.

```text
Current Mission State
        ↓
Possible Responses
        ↓
Simulation
        ↓
Compare Outcomes
        ↓
Risk / Mission Impact
        ↓
Recommended Options
```

Optimization and reinforcement-learning techniques can also be explored within the simulated environment to find better response strategies.

---
# 🛡️ Safety Layer

The CONFLUX Safety Layer provides an additional validation stage for
mission-related recommendations and decisions.

It checks proposed actions against the mission and physical constraints
implemented in the system before they are presented to the operator.

The overall decision flow is:

> **Analysis → Physics Validation → Safety Checks → Human Decision**

The Safety Layer is intended to prevent recommendations that violate
defined mission constraints from being treated as valid operational
options.

CONFLUX does not give an AI model direct control over the spacecraft.
Final operational decisions remain with the human operator.

# 🧰 Technology

| Technology | Role |
|---|---|
| **Python** | Core backend logic, ML workflows, signal analysis, and mission intelligence |
| **FastAPI + Uvicorn** | API services and backend runtime for the mission intelligence system |
| **SQLAlchemy** | Database models and persistence for mission context and results |
| **scikit-learn** | Isolation Forest and anomaly detection for telemetry, wavefront, and environmental signals |
| **NumPy + Pandas** | Feature engineering, numerical modeling, and dataset processing |
| **PyWavelets** | Multi-scale wavefront and signal analysis for transient anomaly detection |
| **OpenCV** | Infrared and thermal image processing for visual anomaly detection |
| **React + Vite** | Mission dashboard and interactive frontend experience |
| **Joblib** | Saving and loading trained detection models |
| **pypdf** | Retrieval and document knowledge handling for the RAG layer |
| **RAG + Knowledge Retrieval** | Grounding mission analysis with technical space-domain context and evidence |
| **Multimodal Fusion** | Combining telemetry, thermal, orbital, weather, and mission signals into a unified assessment |

---

# 🏗️ Architecture

```text
Telemetry ───────┐
Infrared ────────┤
Wavefront ───────┤
Orbital Data ────┤
Space Weather ──┘
        ↓
Individual Analysis
        ↓
Persisted Mission Results
        ↓
Multimodal Fusion
        ↓
Mission-Level Assessment
        ↓
RAG Knowledge Retrieval
        ↓
Grounded Technical Evidence
        ↓
Operational Guidance
```

---

# 📁 Project Structure

```text
CONFLUX/
├── backend/                 # FastAPI app, AI, mission, safety, and physics logic
│   ├── api/                 # REST API route modules
│   ├── database/            # SQLAlchemy models and DB setup
│   ├── intelligence/        # ML training and anomaly detection scripts
│   ├── mission/             # Mission orchestration logic
│   ├── optimization/        # Optimization and response planning
│   ├── physics/             # Orbital and mission physics helpers
│   ├── rag/                 # Retrieval-backed knowledge logic
│   ├── safety/              # Constraint validation layer
│   ├── services/            # Service layer for domain operations
│   └── main.py              # FastAPI application entry point
├── data/                    # Synthetic datasets for telemetry, wavefront, orbital, and weather
│   ├── telemetry/
│   ├── wavefront/
│   ├── space_weather/
│   └── orbital/
├── models/                  # Generated trained model artifacts (.joblib, .pkl)
├── frontend/                # React + Vite mission dashboard
├── tests/                   # Backend and integration tests
├── docs/                    # Project docs and design notes
├── knowledge/               # Space-domain knowledge and grounding material
├── scripts/                 # Utility scripts
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata/configuration
├── README.md                # Setup and usage documentation
├── .gitignore               # Ignored generated files and local artifacts
└── LICENSE                  # Project license
```

---

# ⚙️ How to Run CONFLUX

## Prerequisites

Install the following before running the project:

- **Python 3.10+**
- **Node.js + npm**
- **Git**

> The project uses generated ML model files such as `.joblib` and `.pkl`. These are intentionally kept out of Git in the `.gitignore` file because they are trained output artifacts, not source code.

---

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd CONFLUX
```

This gets the full project and all source files onto your machine.

---

## 2. Set Up the Python Environment

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

This installs the FastAPI backend, ML libraries, data processing tools, and the packages used by the intelligence models.

---

## 3. Train the AI Models First

Before starting the API, you need to create the trained model files in the `models/` directory.

These model files are generated during training and are not committed to Git because they are machine-learning artifacts.

### 3.1 Train the telemetry anomaly detector

```bash
python backend/intelligence/train_telemetry.py
```

This trains an Isolation Forest on spacecraft telemetry and saves the model to `models/telemetry_isolation_forest.joblib`.
It is used to detect abnormal telemetry patterns such as temperature, voltage, current, or pressure spikes.

### 3.2 Train the wavefront detector

```bash
python backend/intelligence/train_wavefront.py
```

This trains the wavefront anomaly detector using normal wavefront observations and saves it to `models/wavefront_detector.pkl`.
It helps detect unusual optical distortion or signal changes across the wavefront sensor data.

### 3.3 Train the space-weather detector

```bash
python backend/intelligence/train_space_weather.py
```

This learns thresholds from normal space-weather behavior and evaluates environmental anomaly detection.
It is used to flag risky solar and radiation conditions that may affect the mission.

### Optional: regenerate synthetic datasets

This step is optional and is only needed if you want fresh synthetic samples for experimentation or to recreate the generated datasets.
It is not required for normal project startup, because the repo already includes the pre-generated CSV files.

```bash
python data/wavefront/generate_dataset.py
python data/space_weather/generate_dataset.py
```

These scripts create synthetic wavefront and space-weather data for experimentation and model testing.
The telemetry dataset is already included in the repo as `data/telemetry/telemetry_dataset_500.csv`, so there is no separate telemetry generator script to rerun here unless you add one yourself.

> If you skip the training steps, the backend may not have the model files it expects at runtime.

---

## 4. Start the Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

This starts the FastAPI backend used for telemetry, orbit, weather, fusion, mission, and RAG endpoints.

### Backend URL

```text
http://127.0.0.1:8000
```

### API Docs

```text
http://127.0.0.1:8000/docs
```

---

## 5. Start the Frontend

Open a new terminal and run:

```bash
cd frontend
npm install
npm run dev
```

This starts the React + Vite dashboard used to visualize mission data and interact with the backend.

Open the URL shown in the terminal, usually:

```text
http://localhost:5173
```

---

## 6. Run the Full Project

Both the backend and frontend should be running at the same time.

```text
┌─────────────────────────┐
│     React + Vite        │
│       Frontend          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      FastAPI API        │
│        Backend          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Mission Data + Analysis │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Multimodal Fusion     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   RAG Knowledge Layer   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Mission Intelligence  │
└─────────────────────────┘
```

Select a mission in the frontend to explore the available modality analyses, fusion assessment, and mission intelligence features.

---

## 7. Optional: Run the Test Suite

From the project root:

```bash
pytest -q
```

From the `frontend` directory:

```bash
npm run lint
npm run build
```

These checks help verify the backend logic and the frontend build are still working correctly.

---

# 🔄 Recommended Development Workflow

Keep two terminals open when working locally:

1. One terminal for the backend (`uvicorn backend.main:app --reload`)
2. One terminal for the frontend (`cd frontend && npm run dev`)

This is the easiest way to develop and test the full system quickly.

---

# 🧪 Running Tests

## Backend

From the project root:

```bash
pytest -q
```

## Frontend

From the `frontend` directory:

```bash
npm run lint
npm run build
```

---

# 🔄 Development Workflow

Keep **two terminals** open during normal development.

### Terminal 1 — Backend

```powershell
cd CONFLUX
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```

### Terminal 2 — Frontend

```bash
cd CONFLUX/frontend
npm run dev
```

The frontend communicates with the local FastAPI backend while the application is running.

---

# 📚 RAG Knowledge Layer

CONFLUX includes a Retrieval-Augmented Generation layer after Multimodal Fusion.

```text
Individual Modalities
        ↓
Multimodal Fusion
        ↓
Mission-Level Assessment
        ↓
RAG Retrieval
        ↓
Relevant Knowledge
        ↓
Technical Interpretation
        ↓
Operational Guidance
```

RAG does **not** replace the existing anomaly detection or Fusion logic.

**Fusion determines what is happening.**

**RAG retrieves relevant technical knowledge to help explain why it may be happening and what should be investigated next.**

The RAG layer uses the current mission context so that retrieved information corresponds to the selected mission.

---

# ⚠️ Important Notes

- **Use a Python virtual environment:** Create and activate `.venv` before installing backend dependencies. The `.venv` directory should remain excluded from Git.
- **Backend and frontend run independently:** Start the FastAPI backend and Vite frontend in separate terminals during development.
- **Backend availability:** The frontend expects the FastAPI backend to be running for API requests, mission data, analysis results, Multimodal Fusion, and RAG functionality.
- **API configuration:** Keep backend API configuration consistent with the frontend API client. If the backend host or port changes, update the corresponding frontend configuration.
- **Environment variables and secrets:** Do not commit API keys, credentials, tokens, or other environment-specific secrets to the repository.
- **Python dependencies:** Install dependencies using `requirements.txt` inside the active virtual environment rather than relying on globally installed packages.
- **Frontend dependencies:** Run `npm install` inside `frontend/` before starting the Vite development server if dependencies are not already installed.
- **Mission context:** Fusion and RAG operations are mission-scoped. Ensure the correct mission is selected before executing or reviewing mission-level results.
- **RAG knowledge:** The RAG layer uses the project's knowledge base to retrieve technical evidence. Retrieved knowledge should not be treated as direct sensor observations; Fusion remains responsible for the mission-level assessment.
- **Development data:** Any demonstration or development knowledge/data included in the repository should not be interpreted as real spacecraft mission data.
- **Analysis pipeline:** Individual modality analysis and Multimodal Fusion should remain independent of the RAG layer. Avoid modifying the existing analysis pipeline when extending the knowledge-retrieval layer.

---

# 📌 Status

> **CONFLUX is Completed**

The goal is to transform large volumes of heterogeneous space data into clear, explainable, and actionable mission intelligence.

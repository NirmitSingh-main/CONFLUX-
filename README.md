# 🛰️ CONFLUX

## Multimodal AI for Real-Time Space Mission Intelligence

CONFLUX is an AI-powered decision-support system designed to help detect, understand, and respond to complex situations during space missions.

Modern spacecraft generate large amounts of information from telemetry, infrared sensors, scientific instruments, orbital tracking systems, and space-weather observations. The challenge is that an important problem may not be visible in one data source alone. Small changes across several systems can combine into a much more serious mission condition.

CONFLUX brings these different sources together and uses AI, signal processing, and physics-based analysis to create a unified view of the spacecraft and its environment.

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
| **Python + FastAPI** | Backend and API services |
| **React + Vite** | Mission dashboard |
| **OpenCV / Computer Vision** | Infrared and thermal image analysis |
| **Time-Series Analysis** | Telemetry analysis |
| **Wavelet Signal Processing** | Wavefront signal analysis |
| **Multimodal Fusion** | Mission-level assessment |
| **Orbital Propagation / Physics** | Orbital and conjunction analysis |
| **Retrieval-Augmented Generation (RAG)** | Grounded technical knowledge retrieval |

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
├── backend/          # Core application, AI, physics and mission logic
├── data/             # Telemetry, infrared, wavefront, orbital and weather data
├── models/           # Trained AI models
├── knowledge/        # Space-domain knowledge
├── frontend/         # Mission dashboard
├── scripts/          # Data and model utilities
├── tests/            # Testing
└── docs/             # Documentation
```

---

# ⚙️ How to Run CONFLUX

## Prerequisites

Install the following before running the project:

- **Python 3.10+**
- **Node.js + npm**
- **Git**

---

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd CONFLUX
```

---

## 2. Set Up the Backend

Create a Python virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI backend:

```bash
uvicorn backend.main:app --reload
```

### Backend

```text
http://127.0.0.1:8000
```

### FastAPI Documentation

```text
http://127.0.0.1:8000/docs
```

---

## 3. Start the Frontend

Open a **new terminal**.

Move into the frontend directory:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Open the local URL displayed by Vite, typically:

```text
http://localhost:5173
```

---

## 4. Run CONFLUX

Both the backend and frontend should be running during development.

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

Select a mission in the frontend to explore the available modality analyses, Fusion assessment, and RAG technical context.

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

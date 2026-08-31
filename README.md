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

CONFLUX does not allow an AI model to directly control the spacecraft.

AI-generated recommendations pass through a deterministic safety layer that checks mission and physical constraints.

> **AI detects and proposes → Physics verifies → Simulation evaluates → Safety validates → Human decides.**

---

# 🤖 AI Mission Copilot

CONFLUX can use an AI mission copilot to convert complex analysis into understandable mission information.

The copilot can explain what happened, summarize the evidence, describe potential risks, and present possible responses.

A knowledge and retrieval layer can provide relevant spacecraft, orbital, scientific, and safety information so that explanations are grounded in available mission knowledge.

---

# 🧰 Technology

| Technology | Role |
|---|---|
| **Python + FastAPI** | Backend and API services |
| **React + Vite** | Mission dashboard |
| **PyTorch + scikit-learn** | AI and machine-learning components |
| **Computer Vision** | Infrared / thermal analysis |
| **Time-Series Analysis** | Telemetry anomaly detection |
| **Wavelet Signal Processing** | Wavefront / signal analysis |
| **Multimodal AI** | Cross-modal mission assessment |
| **Orbital Propagation** | Orbital and conjunction analysis |
| **Physics-Based Analysis** | Mission and orbital reasoning |
| **Simulation / Optimization** | Response analysis |
| **Retrieval-Augmented Generation** | Grounded technical knowledge retrieval |
| **Large Language Models** | Mission copilot capabilities |

---

# 🏗️ Architecture

```text
Telemetry ───────┐
Infrared ────────┤
Wavefront ───────┤
Orbital Data ────┤
Space Weather ──┘
        ↓
 AI + Signal Processing
        ↓
 Physics Analysis
        ↓
 Multimodal Fusion
        ↓
  Mission Intelligence
        ↓
 Simulation / Optimization
        ↓
    Safety Layer
        ↓
  Mission Copilot
        ↓
 Human Operator
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

- Do **not** commit the `.venv` directory.
- Install Python dependencies inside the virtual environment.
- Run the backend and frontend in separate terminals.
- The backend must be running for the frontend to retrieve live mission information.
- Keep environment-specific configuration and secrets out of committed source code.
- If the backend entry point differs from `backend.main:app` in your checkout, use the corresponding FastAPI module path.

---

# 📌 Status

> **CONFLUX is Completed**

The goal is to transform large volumes of heterogeneous space data into clear, explainable, and actionable mission intelligence.

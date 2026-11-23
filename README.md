# 🌱 AgroMind AI: Multi-Agent Smart Farming Assistant

> **Empowering farmers with precision agriculture through coordinated multi-agent intelligence, live meteorological telemetry, and automated agronomic conflict arbitration.**

---

## 📌 Problem Statement & Overview
Modern farmers face unpredictable weather volatility, complex soil nutrient requirements, and pest outbreaks. Single-point AI solutions often give generic advice or recommend actions that clash with real-time environmental factors (e.g., suggesting fertilizer right before a torrential downpour, leading to costly nutrient runoff and chemical pollution).

**AgroMind AI** solves this through a **Multi-Agent Collaborative System** where specialized autonomous agents analyze live weather conditions, soil physics, and crop growth stages. An orchestrator coordinates their findings, detects competing operational priorities, and delivers an arbitrated, safe farming advisory.

---

## 🤖 The Four Autonomous AI Agents

```
                        ┌───────────────────────────────────────────────┐
                        │      Modern Web App (http://localhost:8000)   │
                        └───────────────────────┬───────────────────────┘
                                                │ REST API
                                                ▼
                        ┌───────────────────────────────────────────────┐
                        │      Agent 4: Coordinator & Report Agent       │
                        └───────┬───────────────────────────────┬───────┘
                                │                               │
                Query Weather   ▼               Query Agronomy  ▼
        ┌───────────────────────────────┐       ┌───────────────────────────────┐
        │   Agent 1: Weather Agent      │       │     Agent 2: Crop Agent       │
        │ - Open-Meteo Live API         │       │ - Crop Knowledge Base         │
        │ - Microclimate Hazard Index   │       │ - Soil Drainage & Retention   │
        │ - Rain / Wind / Heat Alerts   │       │ - Growth Stage Nutrients      │
        └───────────────┬───────────────┘       └───────────────┬───────────────┘
                        │                                       │
                        └───────────────────┬───────────────────┘
                                            │
                                            ▼
                        ┌───────────────────────────────────────────────┐
                        │   Agent 3: Farm Recommendation Agent          │
                        │ - Irrigation Schedules                        │
                        │ - Nutrition & Fertilizer Protocols            │
                        │ - Pest & Disease Countermeasures              │
                        │ - Daily Field Operations Dispatch             │
                        └───────────────────┬───────────────────────────┘
                                            │
                                            ▼
                        ┌───────────────────────────────────────────────┐
                        │  Agent 4: Conflict Arbitration & Gemini AI    │
                        │ - Detects conflicting agent recommendations   │
                        │ - Resolves timing & agrochemical safety       │
                        │ - Google Gemini AI Executive Synthesis        │
                        └───────────────────────────────────────────────┘
```

1. **🛰️ Weather Intelligence Agent (`agents/weather_agent.py`)**
   - Fetches live weather and 3-day meteorological forecasts via Open-Meteo API.
   - Computes microclimate hazard indices (heat stress, chilling injury, pathogen incubation humidity, wind drift risks).
2. **🔬 Crop Analysis Agent (`agents/crop_agent.py`)**
   - Evaluates the specific crop variety (Rice, Wheat, Corn, Cotton, Tomato, etc.).
   - Assesses soil physics (Clay, Loam, Sandy, Black Cotton, Red soils) for water retention, compaction, and CEC.
   - Diagnoses stage-dependent physiological needs and pest vulnerabilities.
3. **💡 Farm Recommendation Agent (`agents/recommendation_agent.py`)**
   - Formulates tailored irrigation timing, stage fertilization doses, pest scouting routines, and daily task permissions.
4. **⚖️ Coordinator & Conflict Arbitrator (`agents/coordinator.py`)**
   - Chronological message passing across all agents.
   - **Conflict Detection & Arbitration**: Identifies competing directives (e.g., Urea application scheduled on rain days, or spraying in high winds) and automatically overrides or reschedules them to protect crop health and prevent input waste.
   - Synthesizes the final advisory using **Google Gemini AI** (with an agronomic rule-based fallback).

---

## 🛠️ Tech Stack
- **Backend & API:** FastAPI, Uvicorn, Pydantic
- **AI Engine:** Google Gemini AI (`google-genai` / `gemini-2.5-flash`)
- **Weather Telemetry:** Open-Meteo Live API & Geocoding
- **Frontend / UI:** Modern Responsive Web Application (Tailwind CSS, FontAwesome 6, Vanilla JS) served directly by FastAPI (No Streamlit needed!)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <YOUR_REPO_URL>
cd AgroMind-AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Gemini API
Copy `.env.example` to `.env` and set your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: AgroMind AI features an intelligent fallback engine that works completely offline if no API key is provided!)*

### 4. Launch the Application
```bash
python run_backend.py
```
Open your browser at **`http://localhost:8000`** to view the live dashboard.
Interactive Swagger API documentation is available at **`http://localhost:8000/docs`**.

---

## 📊 Project Structure
```
AgroMind-AI/
├── frontend/                   # Modern responsive Web UI (Tailwind CSS & JS)
│   ├── index.html              # Main dashboard matching Dribbble design
│   └── js/
│       └── app.js              # Client-side API integration & event rendering
├── backend/
│   ├── __init__.py
│   └── main.py                 # FastAPI backend, REST endpoints & static file mounting
├── agents/
│   ├── __init__.py
│   ├── weather_agent.py        # Agent 1: Atmospheric & hazard analysis
│   ├── crop_agent.py           # Agent 2: Agronomic & soil compatibility
│   ├── recommendation_agent.py # Agent 3: Decision support & field action plan
│   └── coordinator.py          # Agent 4: Orchestrator & conflict arbitration
├── services/
│   ├── __init__.py
│   ├── weather_api.py          # Open-Meteo live API integration & geocoding
│   └── gemini_service.py       # Google Gemini AI backend service
├── run_backend.py              # Single launcher for Backend + Frontend
├── requirements.txt            # Lightweight dependencies
├── README.md                   # Hackathon documentation & architecture
└── .gitignore                  # Git exclusions
```

---

## 🌾 Hackathon Highlights
- **No Streamlit Overhead:** Lightweight, blazing-fast single server serving both the REST API and the modern UI.
- **Real-Time Data Integration:** Zero mock dependencies—fetches actual satellite/station weather for any global location.
- **Genuine Agent Communication:** Complete audit trail of inter-agent messages and timestamps displayed live on the dashboard.
- **Automated Conflict Resolution:** Bridges the gap between rigid crop schedules and dynamic environmental conditions.
- **Fail-Safe Architecture:** Guaranteed demo stability even without network access or LLM rate limits.

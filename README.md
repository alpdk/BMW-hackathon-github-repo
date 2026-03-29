# BMW Talent Intelligence Platform

A multi-agent decision-support system for leadership-critical workforce planning at BMW Group.

This project helps decision-makers evaluate **who should be placed into which high-impact role, when, and why**. It combines structured employee and role data with a multi-agent AI pipeline to improve succession planning, internal-vs-external hiring decisions, and development planning.

---

## Why this exists

Leadership decisions are often:
- intuition-heavy
- biased toward “safe” choices
- weak at scenario simulation
- focused on speed instead of long-term fit

This project addresses that by breaking workforce decisions into explainable, modular reasoning steps. Instead of asking one model for one opaque answer, we run a structured pipeline that evaluates:
- role urgency
- employee trajectory
- role-to-person fit
- required development interventions
- final executive action recommendations

The result is a system that improves decision quality, not just automation.

---

## Core use case

This prototype focuses on **leadership-critical workforce planning**.

Given:
- a set of forecasted roles
- a set of internal employee profiles

the system helps answer:
- Which roles are most urgent and strategically exposed?
- Which internal employees are credible successors?
- Where is the internal pipeline not ready in time?
- When should BMW develop internally vs hire externally?
- What development actions should happen now?

---

## Key capabilities

### 1. Load raw employee and role data
The app can load the current structured dataset of:
- employees
- forecasted roles

### 2. Run a multi-agent analysis
The AI pipeline analyzes the raw data and produces:
- prioritized roles
- employee trajectories
- role matches
- development plans
- executive decisions

### 3. Preserve raw data as source of truth
Raw data remains the base layer.
Pipeline output enriches the system with:
- scores
- timing predictions
- match logic
- decision recommendations

### 4. Manage the dataset through the UI
The app includes a **Manage Data** page where users can:
- add employees
- delete employees
- add roles
- delete roles

### 5. Persist state across reloads
Loaded data and the latest analysis can persist locally so the app does not reset every time the page reloads.

---

## System architecture

The system follows a **3-layer architecture**:

### A. Raw input layer
Stable business facts:
- employee profiles
- role definitions
- departments
- skills
- readiness gaps
- context

### B. Pipeline analysis layer
AI-generated reasoning:
- urgency scoring
- trajectory scoring
- role matching
- development planning
- executive recommendations

### C. Display layer
UI-friendly values:
- department names
- readable timelines
- badges
- percentages
- labels for health / urgency / fit

This separation is important:
- raw data = source of truth
- AI output = analysis
- UI = presentation

---

## Multi-agent pipeline

The backend pipeline is composed of five agents:

### 1. Role Forecasting Agent
Determines which roles are most urgent and strategically important.

### 2. Employee Trajectory Agent
Assesses internal employees for growth velocity, readiness horizon, strengths, and gaps.

### 3. Gap Bridging / Matching Agent
Matches internal talent to forecasted roles and recommends:
- internal
- external
- hybrid

### 4. Development Planning Agent
Builds concrete development plans to close critical gaps before role openings.

### 5. Decision Synthesis Agent
Produces executive-ready decisions, key risks, and next steps.

---

## Tech stack

### Frontend
- React
- TypeScript
- Vite
- React Router
- Tailwind / UI components
- Context-based state management

### Backend
- FastAPI
- Python
- JSON-based synthetic dataset
- OpenAI-powered agent orchestration

### Data / persistence
- synthetic JSON source data
- local frontend persistence
- generated pipeline result files

---

## Repository structure

```text
.
├── bmw-backend/
│   ├── data/
│   │   ├── synthetic_data.json
│   │   └── results/
│   ├── pipeline_agents/
│   │   └── pipeline.py
│   ├── routers/
│   │   └── pipeline.py
│   ├── main.py
│   ├── requirements.txt
│   └── railway.toml
│
└── bmw-frontend/
    ├── src/
    │   ├── components/
    │   ├── context/
    │   ├── data/
    │   ├── lib/
    │   ├── pages/
    │   ├── types/
    │   └── App.tsx
    ├── package.json
    └── ...
```

## Running locally

### Prerequisites

Before starting the backend, make sure you have your **own OpenAI API key** available.

This project requires an OpenAI API key for the multi-agent pipeline to run.  
For security reasons, **our API key is not included** in the repository.

Set your own key as an environment variable before starting the backend.

#### macOS / Linux
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

#### Windows (PowerShell)
```bash
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

### Backend

Open a terminal and run:

```bash
cd bmw-backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend should start on: `http://localhost:8000`

### Frontend

Open a second terminal and run:
```bash
cd bmw-frontend
npm install
npm run dev
```

The frontend should start on: `http://localhost:8080`

How to use the app
1. Open the frontend in your browser
2. Click Load Data to fetch the latest employees and roles
3. Click Run Analysis to generate AI insights
4. Use Manage Data if you want to add or remove employees and roles

# BMW Career Intelligence — Backend

Multi-agent FastAPI backend for proactive talent pipeline management.

## Architecture

```
Request → Role Forecast Agent
        → Employee Trajectory Agent  
        → Gap Bridging / Matching Agent
        → Development Plan Agent
        → Decision Synthesis Agent
        → Response
```

Each agent is a focused GPT-4o call with a structured JSON output contract.

## Setup

```bash
# 1. Clone and enter directory
cd bmw-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your OpenAI API key
export OPENAI_API_KEY=sk-...

# 5. Run locally
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/pipeline/run` | Run full multi-agent pipeline |
| GET | `/api/data/employees` | List all employees |
| GET | `/api/data/roles` | List forecasted role openings |
| GET | `/api/data/overview` | Org overview stats |
| GET | `/health` | Health check |

## Pipeline Request Options

```json
{
  "scenario": "supply_chain_crisis | ev_transformation | talent_war | null",
  "filter_department": "d1 | d2 | d3 | d4 | d5 | null",
  "filter_employee_id": "e1 ... e8 | null"
}
```

## Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variable in Railway dashboard:
# OPENAI_API_KEY = sk-...
```

## Data

Synthetic BMW-style dataset in `data/synthetic_data.json`:
- 8 employees across 5 departments
- 5 forecasted role openings
- Org structure with departments and reporting lines
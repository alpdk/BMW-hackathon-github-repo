import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pipeline_agents.pipeline import run_full_pipeline

from datetime import datetime

router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data" / "synthetic_data.json"
RESULTS_DIR = Path(__file__).parent.parent / "data" / "results"
RESULTS_DIR.mkdir(exist_ok=True)

def load_data() -> dict:
    with open(DATA_PATH) as f:
        return json.load(f)


class RunPipelineRequest(BaseModel):
    scenario: Optional[str] = None  # e.g. "supply_chain_crisis", "ev_transformation"
    filter_department: Optional[str] = None  # department id to focus on
    filter_employee_id: Optional[str] = None  # run for a specific employee


@router.post("/pipeline/run")
async def run_pipeline(request: RunPipelineRequest):
    """Run the full multi-agent talent pipeline."""
    try:
        data = load_data()

        # Apply filters if requested
        if request.filter_department:
            data["employees"] = [
                e for e in data["employees"]
                if e["department_id"] == request.filter_department
            ]
            data["forecasted_roles"] = [
                r for r in data["forecasted_roles"]
                if r["department_id"] == request.filter_department
            ]

        if request.filter_employee_id:
            data["employees"] = [
                e for e in data["employees"]
                if e["id"] == request.filter_employee_id
            ]

        # Inject scenario context if provided
        if request.scenario:
            scenario_contexts = {
                "supply_chain_crisis": "ACTIVE SCENARIO: BMW is facing a critical semiconductor and battery material shortage. Supply chain roles are now highest priority. Prioritize candidates with crisis management experience.",
                "ev_transformation": "ACTIVE SCENARIO: BMW has accelerated EV-only production timeline by 2 years. All engineering and production roles must now weight EV experience 2x. Urgency across all technical roles is elevated.",
                "talent_war": "ACTIVE SCENARIO: Tech competitors (Tesla, Apple, Google) are aggressively poaching BMW's digital talent. Retention risk is high. Factor flight risk into all trajectory assessments."
            }
            context = scenario_contexts.get(request.scenario, "")
            if context:
                data["scenario_context"] = context

        result = run_full_pipeline(data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_tag = request.scenario or "default"
        filename = RESULTS_DIR / f"result_{scenario_tag}_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)

        return {"success": True, "data": result, "saved_to": str(filename)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/employees")
async def get_employees():
    """Return all employee profiles."""
    data = load_data()
    return {"employees": data["employees"]}


@router.get("/data/roles")
async def get_roles():
    """Return all forecasted roles."""
    data = load_data()
    return {"roles": data["forecasted_roles"]}


@router.get("/data/overview")
async def get_overview():
    """Return org overview stats."""
    data = load_data()
    return {
        "total_employees": len(data["employees"]),
        "forecasted_openings": len(data["forecasted_roles"]),
        "departments": data["organization"]["departments"],
        "critical_roles": len([r for r in data["forecasted_roles"] if r["priority"] == "critical"])
    }

@router.get("/pipeline/last")
async def get_last_result():
    """Return the most recent saved pipeline result."""
    files = sorted(RESULTS_DIR.glob("result_*.json"))
    if not files:
        raise HTTPException(status_code=404, detail="No saved results found. Run the pipeline first.")
    with open(files[-1]) as f:
        return {"success": True, "data": json.load(f), "file": files[-1].name}
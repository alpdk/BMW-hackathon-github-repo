import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from pipeline_agents.pipeline import run_full_pipeline

router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data" / "synthetic_data.json"
RESULTS_DIR = Path(__file__).parent.parent / "data" / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def load_data() -> dict:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class RunPipelineRequest(BaseModel):
    scenario: Optional[str] = None
    filter_department: Optional[str] = None
    filter_employee_id: Optional[str] = None


@router.post("/pipeline/run")
async def run_pipeline(request: RunPipelineRequest):
    """Run the full multi-agent talent pipeline."""
    try:
        data = load_data()

        if request.filter_department:
            data["employees"] = [
                e for e in data["employees"]
                if e.get("department_id") == request.filter_department
            ]
            data["forecasted_roles"] = [
                r for r in data["forecasted_roles"]
                if r.get("department_id") == request.filter_department
            ]

        if request.filter_employee_id:
            data["employees"] = [
                e for e in data["employees"]
                if e.get("id") == request.filter_employee_id
            ]

        if request.scenario:
            scenario_contexts = {
                "supply_chain_crisis": (
                    "ACTIVE SCENARIO: BMW is facing a critical semiconductor and battery material shortage. "
                    "Supply chain roles are now highest priority. Prioritize candidates with crisis management experience."
                ),
                "ev_transformation": (
                    "ACTIVE SCENARIO: BMW has accelerated EV-only production timeline by 2 years. "
                    "All engineering and production roles must now weight EV experience 2x. "
                    "Urgency across all technical roles is elevated."
                ),
                "talent_war": (
                    "ACTIVE SCENARIO: Tech competitors are aggressively poaching BMW's digital talent. "
                    "Retention risk is high. Factor flight risk into all trajectory assessments."
                ),
            }
            context = scenario_contexts.get(request.scenario, "")
            if context:
                data["scenario_context"] = context

        result = run_full_pipeline(data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_tag = request.scenario or "default"
        filename = RESULTS_DIR / f"result_{scenario_tag}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return {"success": True, "data": result, "saved_to": str(filename)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/employees")
async def get_employees():
    data = load_data()
    return {"employees": data.get("employees", [])}


@router.post("/data/employees")
async def add_employee(employee: Dict[str, Any]):
    data = load_data()
    employees = data.setdefault("employees", [])

    employee_id = employee.get("id")
    if not employee_id:
        raise HTTPException(status_code=400, detail="Employee must include an 'id' field.")

    if any(e.get("id") == employee_id for e in employees):
        raise HTTPException(status_code=400, detail=f"Employee with id '{employee_id}' already exists.")

    employees.append(employee)
    save_data(data)
    return {"success": True, "employee": employee}


@router.delete("/data/employees/{employee_id}")
async def delete_employee(employee_id: str):
    data = load_data()
    employees = data.get("employees", [])
    original_len = len(employees)

    data["employees"] = [e for e in employees if e.get("id") != employee_id]

    if len(data["employees"]) == original_len:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")

    save_data(data)
    return {"success": True, "deleted_id": employee_id}


@router.get("/data/roles")
async def get_roles():
    data = load_data()
    return {"roles": data.get("forecasted_roles", [])}


@router.post("/data/roles")
async def add_role(role: Dict[str, Any]):
    data = load_data()
    roles = data.setdefault("forecasted_roles", [])

    role_id = role.get("id")
    if not role_id:
        raise HTTPException(status_code=400, detail="Role must include an 'id' field.")

    if any(r.get("id") == role_id for r in roles):
        raise HTTPException(status_code=400, detail=f"Role with id '{role_id}' already exists.")

    roles.append(role)
    save_data(data)
    return {"success": True, "role": role}


@router.delete("/data/roles/{role_id}")
async def delete_role(role_id: str):
    data = load_data()
    roles = data.get("forecasted_roles", [])
    original_len = len(roles)

    data["forecasted_roles"] = [r for r in roles if r.get("id") != role_id]

    if len(data["forecasted_roles"]) == original_len:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found.")

    save_data(data)
    return {"success": True, "deleted_id": role_id}


@router.get("/data/overview")
async def get_overview():
    data = load_data()
    roles = data.get("forecasted_roles", [])
    return {
        "total_employees": len(data.get("employees", [])),
        "forecasted_openings": len(roles),
        "departments": data.get("organization", {}).get("departments", []),
        "critical_roles": len([r for r in roles if r.get("priority") == "critical"]),
    }


@router.get("/pipeline/last")
async def get_last_result():
    files = sorted(RESULTS_DIR.glob("result_*.json"))
    if not files:
        raise HTTPException(status_code=404, detail="No saved results found. Run the pipeline first.")

    with open(files[-1], "r", encoding="utf-8") as f:
        return {"success": True, "data": json.load(f), "file": files[-1].name}
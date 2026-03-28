import json
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data" / "synthetic_data.json"


def load_data() -> dict:
    with open(DATA_PATH) as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ── Pydantic Models ────────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    name: str
    current_role: str
    department_id: str
    tenure_years: float
    age: int
    location: str
    performance_ratings: list[float]
    skills: list[str]
    leadership_traits: list[str]
    development_history: list[str] = []
    career_aspiration: str
    mobility: str
    readiness_gaps: list[str] = []
    manager_assessment: str = ""


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    current_role: Optional[str] = None
    department_id: Optional[str] = None
    tenure_years: Optional[float] = None
    age: Optional[int] = None
    location: Optional[str] = None
    performance_ratings: Optional[list[float]] = None
    skills: Optional[list[str]] = None
    leadership_traits: Optional[list[str]] = None
    development_history: Optional[list[str]] = None
    career_aspiration: Optional[str] = None
    mobility: Optional[str] = None
    readiness_gaps: Optional[list[str]] = None
    manager_assessment: Optional[str] = None


class RoleCreate(BaseModel):
    title: str
    department_id: str
    opening_in_months: int
    reason: str
    priority: str  # critical / high / medium
    required_skills: list[str]
    required_leadership_traits: list[str]
    context: str


class RoleUpdate(BaseModel):
    title: Optional[str] = None
    department_id: Optional[str] = None
    opening_in_months: Optional[int] = None
    reason: Optional[str] = None
    priority: Optional[str] = None
    required_skills: Optional[list[str]] = None
    required_leadership_traits: Optional[list[str]] = None
    context: Optional[str] = None


# ── Employee Endpoints ─────────────────────────────────────────────────────────

@router.get("/employees")
async def list_employees():
    """List all employees."""
    data = load_data()
    return {"employees": data["employees"], "total": len(data["employees"])}


@router.get("/employees/{employee_id}")
async def get_employee(employee_id: str):
    """Get a single employee by ID."""
    data = load_data()
    emp = next((e for e in data["employees"] if e["id"] == employee_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")
    return emp


@router.post("/employees", status_code=201)
async def create_employee(employee: EmployeeCreate):
    """Add a new employee."""
    data = load_data()
    new_id = "e" + str(uuid.uuid4())[:8]
    new_employee = {"id": new_id, **employee.model_dump()}
    data["employees"].append(new_employee)
    save_data(data)
    return {"message": "Employee created", "employee": new_employee}


@router.patch("/employees/{employee_id}")
async def update_employee(employee_id: str, updates: EmployeeUpdate):
    """Update specific fields of an employee."""
    data = load_data()
    emp = next((e for e in data["employees"] if e["id"] == employee_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")

    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    emp.update(update_dict)
    save_data(data)
    return {"message": "Employee updated", "employee": emp}


@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    """Remove an employee."""
    data = load_data()
    before = len(data["employees"])
    data["employees"] = [e for e in data["employees"] if e["id"] != employee_id]
    if len(data["employees"]) == before:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")
    save_data(data)
    return {"message": f"Employee '{employee_id}' deleted"}


@router.post("/employees/{employee_id}/rating")
async def add_performance_rating(employee_id: str, rating: float):
    """Append a new performance rating to an employee's history."""
    if not 0 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")
    data = load_data()
    emp = next((e for e in data["employees"] if e["id"] == employee_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")
    emp["performance_ratings"].append(round(rating, 2))
    save_data(data)
    return {"message": "Rating added", "performance_ratings": emp["performance_ratings"]}


@router.post("/employees/{employee_id}/skills")
async def add_skill(employee_id: str, skill: str):
    """Add a skill to an employee."""
    data = load_data()
    emp = next((e for e in data["employees"] if e["id"] == employee_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")
    if skill in emp["skills"]:
        raise HTTPException(status_code=400, detail=f"Skill '{skill}' already exists")
    emp["skills"].append(skill)
    save_data(data)
    return {"message": "Skill added", "skills": emp["skills"]}


@router.delete("/employees/{employee_id}/skills/{skill}")
async def remove_skill(employee_id: str, skill: str):
    """Remove a skill from an employee."""
    data = load_data()
    emp = next((e for e in data["employees"] if e["id"] == employee_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")
    if skill not in emp["skills"]:
        raise HTTPException(status_code=404, detail=f"Skill '{skill}' not found")
    emp["skills"].remove(skill)
    save_data(data)
    return {"message": "Skill removed", "skills": emp["skills"]}


# ── Role Endpoints ─────────────────────────────────────────────────────────────

@router.get("/roles")
async def list_roles():
    """List all forecasted roles."""
    data = load_data()
    return {"roles": data["forecasted_roles"], "total": len(data["forecasted_roles"])}


@router.get("/roles/{role_id}")
async def get_role(role_id: str):
    """Get a single role by ID."""
    data = load_data()
    role = next((r for r in data["forecasted_roles"] if r["id"] == role_id), None)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
    return role


@router.post("/roles", status_code=201)
async def create_role(role: RoleCreate):
    """Add a new forecasted role."""
    data = load_data()
    new_id = "r" + str(uuid.uuid4())[:8]
    new_role = {"id": new_id, **role.model_dump()}
    data["forecasted_roles"].append(new_role)
    save_data(data)
    return {"message": "Role created", "role": new_role}


@router.patch("/roles/{role_id}")
async def update_role(role_id: str, updates: RoleUpdate):
    """Update specific fields of a role."""
    data = load_data()
    role = next((r for r in data["forecasted_roles"] if r["id"] == role_id), None)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")

    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    role.update(update_dict)
    save_data(data)
    return {"message": "Role updated", "role": role}


@router.delete("/roles/{role_id}")
async def delete_role(role_id: str):
    """Remove a forecasted role."""
    data = load_data()
    before = len(data["forecasted_roles"])
    data["forecasted_roles"] = [r for r in data["forecasted_roles"] if r["id"] != role_id]
    if len(data["forecasted_roles"]) == before:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
    save_data(data)
    return {"message": f"Role '{role_id}' deleted"}
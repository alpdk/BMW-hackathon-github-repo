import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = "gpt-4o-mini"


def run_agent(system_prompt: str, user_message: str) -> dict:
    """Run a single agent and return parsed JSON output."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    return json.loads(response.choices[0].message.content)


# ── Agent 1: Role Forecasting ─────────────────────────────────────────────────
ROLE_FORECAST_SYSTEM = """
You are the Role Forecasting Agent for BMW Group's HR intelligence system.
Your job: analyze forecasted role openings and identify which ones are most urgent
and strategically critical given the organizational context.

Return a JSON object with this exact structure:
{
  "prioritized_roles": [
    {
      "role_id": "string",
      "title": "string",
      "urgency_score": 0-100,
      "strategic_importance": "string (1-2 sentences)",
      "opening_in_months": number,
      "key_requirements_summary": ["string", ...]
    }
  ],
  "analysis_summary": "string (2-3 sentences on overall org risk)"
}

Order by urgency_score descending. Be specific and realistic — this is for senior BMW HR executives.
"""


def role_forecast_agent(org_data: dict, roles: list) -> dict:
    prompt = f"""
Organization: {json.dumps(org_data, indent=2)}
Forecasted Roles: {json.dumps(roles, indent=2)}

Analyze these forecasted openings. Score urgency based on timeline, business criticality,
and strategic context. Return prioritized roles with clear reasoning.
"""
    return run_agent(ROLE_FORECAST_SYSTEM, prompt)


# ── Agent 2: Employee Trajectory ──────────────────────────────────────────────
TRAJECTORY_SYSTEM = """
You are the Employee Trajectory Agent for BMW Group's HR intelligence system.
Your job: analyze each employee's current profile, growth trajectory, and predict
their readiness for leadership roles over the next 6-18 months.

Return a JSON object with this exact structure:
{
  "employee_trajectories": [
    {
      "employee_id": "string",
      "name": "string",
      "current_role": "string",
      "trajectory_score": 0-100,
      "readiness_horizon_months": number,
      "growth_velocity": "high|medium|low",
      "key_strengths": ["string", ...],
      "critical_gaps": ["string", ...],
      "trajectory_summary": "string (2 sentences)"
    }
  ]
}

Be honest about gaps. Not every employee is ready — say so clearly.
"""


def trajectory_agent(employees: list) -> dict:
    prompt = f"""
Employees: {json.dumps(employees, indent=2)}

Analyze each employee's career trajectory. Assess their growth velocity based on
performance trends, development investments, and manager assessments.
Predict realistic readiness horizons.
"""
    return run_agent(TRAJECTORY_SYSTEM, prompt)


# ── Agent 3: Gap Bridging / Matching ──────────────────────────────────────────
MATCHING_SYSTEM = """
You are the Gap Bridging Agent for BMW Group's HR intelligence system.
Your job: match employee trajectories to forecasted role openings. Identify the best
internal candidates for each role, explain fit and gaps, and flag roles where
internal talent is insufficient.

Return a JSON object with this exact structure:
{
  "role_matches": [
    {
      "role_id": "string",
      "role_title": "string",
      "recommendation": "internal|external|hybrid",
      "top_candidates": [
        {
          "employee_id": "string",
          "name": "string",
          "fit_score": 0-100,
          "will_be_ready_in_months": number,
          "match_reasoning": "string (2-3 sentences)",
          "gaps_to_close": ["string", ...]
        }
      ],
      "external_hire_needed": true|false,
      "external_hire_reasoning": "string or null"
    }
  ],
  "overall_pipeline_health": "strong|moderate|at-risk",
  "pipeline_summary": "string (2-3 sentences)"
}

Be selective — only include candidates with genuine fit. Max 2 candidates per role.
"""


def matching_agent(prioritized_roles: list, trajectories: list) -> dict:
    prompt = f"""
Prioritized Roles: {json.dumps(prioritized_roles, indent=2)}
Employee Trajectories: {json.dumps(trajectories, indent=2)}

Match employees to roles. Consider timing — if a role opens in 6 months but an employee
needs 12 months of development, flag this clearly. Recommend external hire where internal
pipeline is insufficient.
"""
    return run_agent(MATCHING_SYSTEM, prompt)


# ── Agent 4: Development Plan ─────────────────────────────────────────────────
DEVELOPMENT_SYSTEM = """
You are the Development Planning Agent for BMW Group's HR intelligence system.
Your job: for each internal candidate match, generate a concrete, time-bound development
plan that closes identified gaps before the role opens.

Return a JSON object with this exact structure:
{
  "development_plans": [
    {
      "employee_id": "string",
      "employee_name": "string",
      "target_role_id": "string",
      "target_role_title": "string",
      "timeline_months": number,
      "interventions": [
        {
          "type": "training|assignment|mentoring|exposure",
          "title": "string",
          "description": "string (1-2 sentences)",
          "duration_months": number,
          "gap_addressed": "string",
          "priority": "critical|high|medium"
        }
      ],
      "success_metrics": ["string", ...],
      "risk_if_not_done": "string (1 sentence)"
    }
  ]
}

Make interventions specific and realistic for BMW's context. Not generic HR platitudes.
"""


def development_agent(matches: list, employees: list) -> dict:
    prompt = f"""
Role Matches (internal candidates only): {json.dumps(matches, indent=2)}
Employee Profiles: {json.dumps(employees, indent=2)}

Generate concrete development plans for each internal candidate.
Plans must close specific gaps before the target role opens.
Interventions should be realistic within BMW's L&D capabilities.
"""
    return run_agent(DEVELOPMENT_SYSTEM, prompt)


# ── Agent 5: Decision Synthesis ───────────────────────────────────────────────
DECISION_SYSTEM = """
You are the Decision Synthesis Agent for BMW Group's HR intelligence system.
Your job: synthesize all upstream agent outputs into a final executive-ready
talent pipeline recommendation. This goes to senior HR leadership.

Return a JSON object with this exact structure:
{
  "executive_summary": "string (3-4 sentences — the key message)",
  "pipeline_health": "strong|moderate|at-risk",
  "decisions": [
    {
      "role_id": "string",
      "role_title": "string",
      "recommended_action": "string (one clear sentence)",
      "action_type": "develop_internal|hire_external|develop_internal_and_hire_external",
      "primary_candidate": "string or null (employee name)",
      "urgency": "immediate|3-months|6-months|12-months",
      "confidence": "high|medium|low",
      "key_risk": "string (1 sentence)",
      "next_step": "string (specific action BMW HR should take this week)"
    }
  ],
  "top_hidden_talent": [
    {
      "employee_id": "string",
      "name": "string",
      "insight": "string (why this person is worth watching)"
    }
  ],
  "org_risks": ["string", ...]
}

Be direct. Senior executives need clear recommendations, not hedged analysis.
"""


def decision_agent(forecast: dict, trajectories: dict, matches: dict, dev_plans: dict) -> dict:
    prompt = f"""
Role Forecast: {json.dumps(forecast, indent=2)}
Employee Trajectories: {json.dumps(trajectories, indent=2)}
Role Matches: {json.dumps(matches, indent=2)}
Development Plans: {json.dumps(dev_plans, indent=2)}

Synthesize everything into a final executive recommendation.
Make clear decisions. Flag the most critical risks. Identify any hidden talent worth highlighting.
"""
    return run_agent(DECISION_SYSTEM, prompt)


# ── Full Pipeline ─────────────────────────────────────────────────────────────
def run_full_pipeline(data: dict) -> dict:
    org = data["organization"]
    roles = data["forecasted_roles"]
    employees = data["employees"]

    # Agent 1
    forecast_result = role_forecast_agent(org, roles)

    # Agent 2
    trajectory_result = trajectory_agent(employees)

    # Agent 3
    match_result = matching_agent(
        forecast_result["prioritized_roles"],
        trajectory_result["employee_trajectories"]
    )

    # Agent 4 — only pass roles with internal candidates
    internal_matches = [
        r for r in match_result["role_matches"]
        if r["recommendation"] in ("internal", "hybrid") and r["top_candidates"]
    ]
    dev_result = development_agent(internal_matches, employees)

    # Agent 5
    decision_result = decision_agent(
        forecast_result, trajectory_result, match_result, dev_result
    )

    return {
        "agents": {
            "role_forecast": forecast_result,
            "employee_trajectories": trajectory_result,
            "role_matches": match_result,
            "development_plans": dev_result,
            "final_decision": decision_result
        }
    }

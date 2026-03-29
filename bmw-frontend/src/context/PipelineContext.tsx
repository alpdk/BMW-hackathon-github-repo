import React, { createContext, useContext, useState, useCallback } from "react";
import { getLastPipeline, runPipeline, getEmployees, getRoles, type RunPipelineRequest } from "@/lib/api";
import {
  mapForecastedRolesFromRaw,
  mapEmployeeTrajectoriesFromRaw,
  mapRoleMatches,
  mapDevelopmentInterventions,
  mapExecutiveDecisions,
  deriveExecutiveSummary,
} from "@/lib/mappers";
import type {
  ForecastedRole,
  EmployeeTrajectory,
  RoleMatch,
  DevelopmentIntervention,
  ExecutiveDecision,
  ExecutiveSummaryData,
} from "@/types/display";
import { toast } from "sonner";

interface PipelineState {
  forecastedRoles: ForecastedRole[];
  employeeTrajectories: EmployeeTrajectory[];
  roleMatches: RoleMatch[];
  developmentInterventions: DevelopmentIntervention[];
  executiveDecisions: ExecutiveDecision[];
  executiveSummary: ExecutiveSummaryData;
  isLoading: boolean;
  isRunning: boolean;
  error: string | null;
  isUsingDemoData: boolean;
  runAnalysis: (params?: RunPipelineRequest) => Promise<void>;
  refreshData: () => Promise<void>;
  loadRawData: () => Promise<void>;
}

const EMPTY_EXEC_SUMMARY: ExecutiveSummaryData = {
  pipelineHealth: 0,
  pipelineHealthLabel: "Not assessed",
  totalForecastedRoles: 0,
  urgentRoles: 0,
  internalReady: 0,
  externalRequired: 0,
  hybridApproach: 0,
  topRisks: [],
  hiddenTalent: [],
  analysisTimestamp: null,
  executiveSummaryText: "",
};

const PipelineContext = createContext<PipelineState | undefined>(undefined);

async function fetchRawData(): Promise<{ employees: any[] | null; roles: any[] | null }> {
  try {
    const [empRes, roleRes] = await Promise.all([getEmployees(), getRoles()]);

    console.log("🔍 RAW API RESPONSES");
    console.log("Employees response:", empRes);
    console.log("Roles response:", roleRes);

    const employees = Array.isArray(empRes)
      ? empRes
      : (empRes?.employees ?? empRes?.data?.employees ?? empRes?.data ?? null);

    const roles = Array.isArray(roleRes)
      ? roleRes
      : (roleRes?.roles ?? roleRes?.data?.roles ?? roleRes?.forecasted_roles ?? roleRes?.data ?? null);

    console.log("🧩 PARSED RAW DATA");
    console.log("Parsed employees:", employees);
    console.log("Parsed roles:", roles);

    if (!employees || !Array.isArray(employees)) {
      console.warn("⚠ Employees parsing failed or returned non-array");
    }

    if (!roles || !Array.isArray(roles)) {
      console.warn("⚠ Roles parsing failed or returned non-array");
    }

    return { employees, roles };
  } catch (err) {
    console.error("❌ fetchRawData failed:", err);
    return { employees: null, roles: null };
  }
}

function parsePipelineResponse(
  pipelineData: any,
  rawEmployees: any[] | null,
  rawRoles: any[] | null
): Omit<PipelineState, "isLoading" | "isRunning" | "error" | "isUsingDemoData" | "runAnalysis" | "refreshData" | "loadRawData"> {
  const agents = pipelineData?.data?.agents ?? pipelineData?.agents ?? pipelineData ?? {};

  const roleForecast = agents?.role_forecast ?? {};
  const trajectories = agents?.employee_trajectories ?? {};
  const matches = agents?.role_matches ?? {};
  const devPlans = agents?.development_plans ?? {};
  const finalDecision = agents?.final_decision ?? {};

  const pipelineRoles =
    roleForecast?.prioritized_roles ??
    roleForecast?.roles ??
    roleForecast?.forecasted_roles ??
    roleForecast?.data ??
    [];

  const pipelineTrajectories =
    trajectories?.employee_trajectories ??
    trajectories?.employees ??
    trajectories?.trajectories ??
    trajectories?.data ??
    [];

  const forecastedRoles =
    rawRoles && rawRoles.length > 0
      ? mapForecastedRolesFromRaw(rawRoles, pipelineRoles)
      : [];

  const employeeTrajectories =
    rawEmployees && rawEmployees.length > 0
      ? mapEmployeeTrajectoriesFromRaw(rawEmployees, pipelineTrajectories)
      : [];

  const roleMatches = mapRoleMatches(
    matches?.role_matches ?? matches?.matches ?? matches?.data ?? []
  );

  const developmentInterventions = mapDevelopmentInterventions(
    devPlans?.development_plans ?? devPlans?.interventions ?? devPlans?.plans ?? devPlans?.data ?? []
  );

  const executiveDecisions = mapExecutiveDecisions(
    finalDecision?.decisions ?? finalDecision?.recommendations ?? finalDecision?.data ?? []
  );

  const executiveSummary = deriveExecutiveSummary(
    forecastedRoles,
    roleMatches,
    executiveDecisions,
    {
      pipeline_health: finalDecision?.pipeline_health ?? matches?.overall_pipeline_health,
      executive_summary: finalDecision?.executive_summary,
      org_risks: finalDecision?.org_risks,
      top_hidden_talent: finalDecision?.top_hidden_talent,
    }
  );

  return {
    forecastedRoles,
    employeeTrajectories,
    roleMatches,
    developmentInterventions,
    executiveDecisions,
    executiveSummary,
  };
}

export function PipelineProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<{
    forecastedRoles: ForecastedRole[];
    employeeTrajectories: EmployeeTrajectory[];
    roleMatches: RoleMatch[];
    developmentInterventions: DevelopmentIntervention[];
    executiveDecisions: ExecutiveDecision[];
    executiveSummary: ExecutiveSummaryData;
    isLoading: boolean;
    isRunning: boolean;
    error: string | null;
    isUsingDemoData: boolean;
  }>({
    forecastedRoles: [],
    employeeTrajectories: [],
    roleMatches: [],
    developmentInterventions: [],
    executiveDecisions: [],
    executiveSummary: EMPTY_EXEC_SUMMARY,
    isLoading: false,
    isRunning: false,
    error: null,
    isUsingDemoData: false,
  });

  const loadRawData = useCallback(async () => {
    setState((s) => ({ ...s, isLoading: true, error: null }));

    try {
      const rawData = await fetchRawData();
      const parsed = parsePipelineResponse({}, rawData.employees, rawData.roles);

      setState((s) => ({
        ...s,
        ...parsed,
        roleMatches: [],
        developmentInterventions: [],
        executiveDecisions: [],
        executiveSummary: deriveExecutiveSummary(parsed.forecastedRoles, [], [], {}),
        isLoading: false,
      }));

      toast.success("Raw data loaded");
    } catch (err: any) {
      const msg = err?.message ?? "Failed to load raw data";
      setState((s) => ({ ...s, isLoading: false, error: msg }));
      toast.error("Failed to load raw data", { description: msg });
    }
  }, []);

  const refreshData = useCallback(async () => {
    setState((s) => ({ ...s, isLoading: true, error: null }));

    try {
      const [pipelineResponse, rawData] = await Promise.all([
        getLastPipeline().catch(() => null),
        fetchRawData(),
      ]);

      if (!pipelineResponse || (pipelineResponse?.success === false && !pipelineResponse?.data)) {
        const parsed = parsePipelineResponse({}, rawData.employees, rawData.roles);
        setState((s) => ({
          ...s,
          ...parsed,
          roleMatches: [],
          developmentInterventions: [],
          executiveDecisions: [],
          executiveSummary: deriveExecutiveSummary(parsed.forecastedRoles, [], [], {}),
          isLoading: false,
        }));
        return;
      }

      const parsed = parsePipelineResponse(pipelineResponse, rawData.employees, rawData.roles);
      setState((s) => ({ ...s, ...parsed, isLoading: false }));
    } catch (err: any) {
      const msg = err?.message ?? "Failed to refresh data";
      setState((s) => ({ ...s, isLoading: false, error: msg }));
      toast.error("Failed to refresh data", { description: msg });
    }
  }, []);

  const runAnalysis = useCallback(async (params: RunPipelineRequest = {}) => {
    setState((s) => ({ ...s, isRunning: true, error: null }));

    try {
      const [pipelineResponse, rawData] = await Promise.all([
        runPipeline(params),
        fetchRawData(),
      ]);

      const parsed = parsePipelineResponse(pipelineResponse, rawData.employees, rawData.roles);
      setState((s) => ({ ...s, ...parsed, isRunning: false }));
      toast.success("Analysis complete — data updated across all views");
    } catch (err: any) {
      const msg = err?.message ?? "Failed to run analysis";
      setState((s) => ({ ...s, isRunning: false, error: msg }));
      toast.error("Analysis failed", { description: msg });
    }
  }, []);

  return (
    <PipelineContext.Provider
      value={{
        ...state,
        runAnalysis,
        refreshData,
        loadRawData,
      }}
    >
      {children}
    </PipelineContext.Provider>
  );
}

export function usePipeline() {
  const ctx = useContext(PipelineContext);
  if (!ctx) throw new Error("usePipeline must be used within PipelineProvider");
  return ctx;
}
import { FALLBACK_ANALYSES, FALLBACK_CASES, fallbackAcmePlan, localExecute } from "./fallback"
import type {
  ActionPlan,
  ActionResult,
  AnalyzeResponse,
  Case,
  DataSource,
} from "../types/api"

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

export function apiBase(): string {
  const configured = import.meta.env.VITE_API_BASE?.trim()
  const base = configured && configured.length > 0 ? configured : "http://127.0.0.1:8000"
  return base.replace(/\/$/, "")
}

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError && error.message.trim()) {
    return error.message
  }
  return "The request failed safely"
}

function shouldFallback(error: unknown): boolean {
  if (!(error instanceof ApiError)) {
    return true
  }
  return error.status === 0 || error.status >= 500
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${apiBase()}${path}`, {
      ...init,
      signal: init?.signal ?? AbortSignal.timeout(8000),
      headers: {
        accept: "application/json",
        ...(init?.body ? { "content-type": "application/json" } : {}),
        ...init?.headers,
      },
    })
  } catch {
    throw new ApiError("The decision service could not be reached.", 0)
  }

  if (!response.ok) {
    throw new ApiError(await readError(response), response.status)
  }
  return (await response.json()) as T
}

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { error?: unknown }
    if (typeof body.error === "string" && body.error.trim()) {
      return body.error
    }
  } catch {
    return "The request failed safely"
  }
  return "The request failed safely"
}

export async function loadCases(): Promise<{ cases: Case[]; source: DataSource }> {
  try {
    const cases = await request<Case[]>("/api/cases")
    if (cases.length === 0) {
      return { cases: FALLBACK_CASES, source: "fallback" }
    }
    return { cases, source: "api" }
  } catch {
    return { cases: FALLBACK_CASES, source: "fallback" }
  }
}

export async function loadAnalysis(
  caseId: string,
): Promise<{ analysis: AnalyzeResponse; source: DataSource }> {
  try {
    const analysis = await request<AnalyzeResponse>("/api/analyze", {
      method: "POST",
      body: JSON.stringify({ case_id: caseId }),
    })
    return { analysis, source: "api" }
  } catch (error) {
    const mock = FALLBACK_ANALYSES[caseId]
    if (mock && shouldFallback(error)) {
      return { analysis: mock, source: "fallback" }
    }
    throw error
  }
}

export async function loadPlan(
  caseId: string,
): Promise<{ plan: ActionPlan; source: DataSource }> {
  try {
    const plan = await request<ActionPlan>("/api/actions/plan", {
      method: "POST",
      body: JSON.stringify({ case_id: caseId }),
    })
    return { plan, source: "api" }
  } catch (error) {
    if (caseId === "acme-sso-rollout" && shouldFallback(error)) {
      return { plan: fallbackAcmePlan(), source: "fallback" }
    }
    throw error
  }
}

export async function runPlan(
  plan: ActionPlan,
  source: DataSource,
): Promise<{ result: ActionResult; source: DataSource }> {
  if (source === "fallback") {
    return { result: localExecute(plan), source: "fallback" }
  }
  const result = await request<ActionResult>("/api/actions/execute", {
    method: "POST",
    body: JSON.stringify({ plan_id: plan.plan_id, approved: true }),
  })
  return { result, source: "api" }
}

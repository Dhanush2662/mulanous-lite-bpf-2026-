import type {
  ActionPlan,
  ActionResult,
  AnalyzeResponse,
  Case,
  EvidenceRecord,
  InvestigateResponse,
} from "@/types/api";

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function apiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  const base =
    configured && configured.length > 0
      ? configured
      : "http://127.0.0.1:8000";
  return base.replace(/\/$/, "");
}

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError && error.message.trim()) {
    return error.message;
  }
  return "The request failed safely";
}

export function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}${path}`, {
      ...init,
      headers: {
        accept: "application/json",
        ...(init?.body ? { "content-type": "application/json" } : {}),
        ...init?.headers,
      },
    });
  } catch (error) {
    if (isAbortError(error)) {
      throw error;
    }
    throw new ApiError("The decision service could not be reached.", 0);
  }

  if (!response.ok) {
    throw new ApiError(await readError(response), response.status);
  }

  return (await response.json()) as T;
}

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { error?: unknown };
    if (typeof body.error === "string" && body.error.trim()) {
      return body.error;
    }
  } catch {
    return "The request failed safely";
  }
  return "The request failed safely";
}

export function getCases(signal?: AbortSignal): Promise<Case[]> {
  return request<Case[]>("/api/cases", { signal });
}

export function getCase(caseId: string, signal?: AbortSignal): Promise<Case> {
  return request<Case>(`/api/cases/${encodeURIComponent(caseId)}`, { signal });
}

export function getCaseEvidence(
  caseId: string,
  signal?: AbortSignal,
  filters?: { source?: string; q?: string },
): Promise<EvidenceRecord[]> {
  const params = new URLSearchParams();
  if (filters?.source) {
    params.set("source", filters.source);
  }
  if (filters?.q) {
    params.set("q", filters.q);
  }
  const query = params.toString();
  const suffix = query ? `?${query}` : "";
  return request<EvidenceRecord[]>(
    `/api/cases/${encodeURIComponent(caseId)}/evidence${suffix}`,
    { signal },
  );
}

export function getEvidence(
  evidenceId: string,
  signal?: AbortSignal,
): Promise<EvidenceRecord> {
  return request<EvidenceRecord>(
    `/api/evidence/${encodeURIComponent(evidenceId)}`,
    { signal },
  );
}

export function analyzeCase(
  caseId: string,
  signal?: AbortSignal,
): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ case_id: caseId }),
    signal,
  });
}

export function planAction(
  caseId: string,
  signal?: AbortSignal,
): Promise<ActionPlan> {
  return request<ActionPlan>("/api/actions/plan", {
    method: "POST",
    body: JSON.stringify({ case_id: caseId }),
    signal,
  });
}

export function executeAction(
  planId: string,
  signal?: AbortSignal,
): Promise<ActionResult> {
  return request<ActionResult>("/api/actions/execute", {
    method: "POST",
    body: JSON.stringify({ plan_id: planId, approved: true }),
    signal,
  });
}

export function investigateCase(
  caseId: string,
  message: string,
  signal?: AbortSignal,
): Promise<InvestigateResponse> {
  return request<InvestigateResponse>("/api/investigate", {
    method: "POST",
    body: JSON.stringify({ case_id: caseId, message }),
    signal,
  });
}

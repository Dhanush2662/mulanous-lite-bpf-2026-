import type { Domain } from "../types/api"

const SOURCE_LABELS: Record<string, string> = {
  crm: "CRM",
  jira: "Jira",
  slack: "Slack",
  meetings: "Meetings",
  erp: "ERP",
  schedule: "Production",
  inventory: "Inventory",
  quality: "Quality",
}

export const CONNECTED_SYSTEMS = [
  "CRM",
  "Jira",
  "Slack",
  "Meetings",
  "ERP",
  "Production",
  "Inventory",
  "Quality",
] as const

export function sourceLabel(source: string): string {
  return SOURCE_LABELS[source] ?? source
}

export function challengeLabel(result: string): string {
  return result.replaceAll("_", " ")
}

export function progressSteps(domain: Domain): string[] {
  if (domain === "manufacturing") {
    return [
      "Collecting ERP evidence",
      "Collecting production evidence",
      "Collecting inventory evidence",
      "Collecting quality evidence",
      "Checking contradictions",
      "Forming decision",
    ]
  }
  if (domain === "logistics") {
    return ["Collecting evidence", "Checking contradictions", "Forming decision"]
  }
  return [
    "Collecting CRM evidence",
    "Collecting Jira evidence",
    "Collecting Slack evidence",
    "Collecting meeting evidence",
    "Checking contradictions",
    "Forming decision",
  ]
}

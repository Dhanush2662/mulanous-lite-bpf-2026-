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

const DOMAIN_SOURCES: Record<Domain, readonly string[]> = {
  software: ["CRM", "Jira", "Slack", "Meetings"],
  manufacturing: ["ERP", "Production", "Inventory", "Quality"],
  logistics: ["ERP", "Inventory"],
}

export function domainSources(domain: Domain): readonly string[] {
  return DOMAIN_SOURCES[domain]
}

export function accountRole(domain: Domain): string {
  if (domain === "manufacturing") {
    return "Manufacturing partner"
  }
  if (domain === "logistics") {
    return "Logistics partner"
  }
  return "Customer account"
}

export function showsToday(urgency: string): boolean {
  return /\btoday\b/i.test(urgency)
}

export function formatObserved(value: string | null): string {
  if (!value) {
    return "No timestamp"
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  const formatted = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "UTC",
  }).format(date)
  return formatted.replace(/,([^,]*)$/, " ·$1")
}

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

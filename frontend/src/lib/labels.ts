const SOURCE_LABELS: Record<string, string> = {
  crm: "CRM",
  jira: "Jira",
  slack: "Slack",
  meetings: "Meetings",
  erp: "ERP",
  schedule: "Schedule",
  inventory: "Inventory",
  quality: "Quality",
};

const SOURCE_ORDER = [
  "crm",
  "jira",
  "slack",
  "meetings",
  "erp",
  "schedule",
  "inventory",
  "quality",
];

export function sourceLabel(source: string): string {
  return SOURCE_LABELS[source] ?? source;
}

export function uniqueSources(sources: string[]): string[] {
  const present = new Set(sources);
  const ordered = SOURCE_ORDER.filter((source) => present.has(source));
  const extras = [...present].filter((source) => !SOURCE_ORDER.includes(source));
  extras.sort();
  return [...ordered, ...extras];
}

export function formatObservedAt(value: string | null): string {
  if (!value) {
    return "No timestamp";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const formatted = new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(date);
  return `${formatted} UTC`;
}

export function challengeLabel(result: string): string {
  return result.replaceAll("_", " ");
}

export function patternLabel(pattern: string): string {
  return pattern.replaceAll("_", " ");
}

export function queueStatusLabel(status: string): string {
  return status.toUpperCase();
}

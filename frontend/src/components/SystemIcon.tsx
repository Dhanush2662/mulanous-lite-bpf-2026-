export function SystemIcon({ name }: { name: string }) {
  return (
    <svg className="system-icon" viewBox="0 0 24 24" aria-hidden="true">
      {paths(name)}
    </svg>
  )
}

function paths(name: string) {
  switch (name) {
    case "CRM":
      return (
        <>
          <circle cx="12" cy="8" r="3" />
          <path d="M5 19c1.4-3 3.8-4.5 7-4.5S17.6 16 19 19" />
        </>
      )
    case "Jira":
      return <path d="M5 7h14v4H9v2h8v4H5" />
    case "Slack":
      return (
        <>
          <path d="M8 4v8" />
          <path d="M16 12v8" />
          <path d="M4 8h8" />
          <path d="M12 16h8" />
        </>
      )
    case "Meetings":
      return (
        <>
          <rect x="4" y="6" width="16" height="12" />
          <path d="M8 6V4h8v2" />
        </>
      )
    case "ERP":
      return (
        <>
          <rect x="4" y="4" width="7" height="7" />
          <rect x="13" y="4" width="7" height="7" />
          <rect x="4" y="13" width="7" height="7" />
          <rect x="13" y="13" width="7" height="7" />
        </>
      )
    case "Production":
      return <path d="M4 16V8l5 3V8l5 3V8l6 4v4H4z" />
    case "Inventory":
      return (
        <>
          <path d="M4 8l8-4 8 4-8 4-8-4z" />
          <path d="M4 8v8l8 4 8-4V8" />
          <path d="M12 12v8" />
        </>
      )
    default:
      return (
        <>
          <circle cx="12" cy="12" r="7" />
          <path d="M12 8v4l3 2" />
        </>
      )
  }
}

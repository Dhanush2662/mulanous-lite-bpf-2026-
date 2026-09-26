import { useNavigate } from "react-router-dom"

import type { Case } from "../../types/api"

export function AttentionQueue({ cases }: { cases: Case[] }) {
  const navigate = useNavigate()
  const groups = groupByDomain(cases)

  if (cases.length === 0) {
    return (
      <p className="status-copy" role="status">
        The attention queue is empty.
      </p>
    )
  }

  return (
    <div className="queue">
      {groups.map((group) => (
        <section key={group.domain} className="queue-section">
          <h2>{group.domain.toUpperCase()}</h2>
          <ul>
            {group.items.map((item) => (
              <li key={item.id} className={item.queue_status === "dismissed" ? "is-quiet" : ""}>
                <div className="queue-copy">
                  <p className="account">{item.account}</p>
                  <p className="claim">{item.claim}</p>
                  <p className="meta">
                    {item.urgency}
                    {" · "}
                    {item.source_count} sources
                    {item.disposition ? ` · ${item.disposition}` : ""}
                    {item.queue_status === "dismissed" ? " · Dismissed" : ""}
                    {item.last_action_status === "executed" ? " · Action executed" : ""}
                  </p>
                </div>
                <button
                  type="button"
                  className="open-button"
                  onClick={() => navigate(`/cases/${item.id}`, { state: { preview: item } })}
                >
                  OPEN
                </button>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  )
}

function groupByDomain(cases: Case[]): { domain: string; items: Case[] }[] {
  const groups: { domain: string; items: Case[] }[] = []
  for (const item of cases) {
    const last = groups[groups.length - 1]
    if (!last || last.domain !== item.domain) {
      groups.push({ domain: item.domain, items: [item] })
    } else {
      last.items.push(item)
    }
  }
  return groups
}

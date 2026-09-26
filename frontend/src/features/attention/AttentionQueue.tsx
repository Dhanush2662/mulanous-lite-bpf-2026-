import { useNavigate } from "react-router-dom"

import { SourceChips } from "../../components/SourceChips"
import { accountRole, domainSources, showsToday } from "../labels"
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
            {group.items.map((item, index) => {
              const sources = domainSources(item.domain)
              const lead = group.domain === "software" && index === 0
              return (
                <li
                  key={item.id}
                  className={[
                    lead ? "is-lead" : "",
                    item.queue_status === "dismissed" ? "is-quiet" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                >
                  <div className="queue-copy">
                    <p className="account">{item.account}</p>
                    <p className="role">{accountRole(item.domain)}</p>
                    <p className="claim">{item.claim}</p>
                    <SourceChips names={sources} />
                    <p className="checkpoint">{item.urgency}</p>
                  </div>
                  <div className="queue-side">
                    {showsToday(item.urgency) ? <span className="today">Today</span> : null}
                    <span className="source-count">{sources.length} sources</span>
                    <button
                      type="button"
                      className="open-button"
                      onClick={() => navigate(`/cases/${item.id}`, { state: { preview: item } })}
                    >
                      OPEN
                    </button>
                  </div>
                </li>
              )
            })}
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

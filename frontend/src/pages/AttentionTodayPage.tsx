import { AppHeader } from "../components/AppHeader"
import { FallbackNote } from "../components/FallbackNote"
import { AttentionQueue } from "../features/attention/AttentionQueue"
import { CONNECTED_SYSTEMS } from "../features/labels"
import { useAttentionQueue } from "../hooks/useAttentionQueue"

export function AttentionTodayPage() {
  const queue = useAttentionQueue()

  return (
    <>
      <AppHeader />
      <main className="page">
        <div className="attention-head">
          <h1>What needs my attention today?</h1>
          <p className="demo-mark">SYNTHETIC DEMO</p>
        </div>
        <section className="systems">
          <h2>CONNECTED SYSTEMS</h2>
          <ul>
            {CONNECTED_SYSTEMS.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        </section>
        {queue.loading ? (
          <p className="status-copy" role="status">
            Loading the attention queue.
          </p>
        ) : (
          <>
            <FallbackNote
              source={queue.source}
              text="Local fallback. The decision service did not return the queue."
            />
            <AttentionQueue cases={queue.cases} />
          </>
        )}
      </main>
    </>
  )
}

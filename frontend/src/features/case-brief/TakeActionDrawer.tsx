import { useEffect, useState } from "react"

import { errorMessage, loadPlan, runPlan } from "../../api/client"
import { Drawer } from "../../components/Drawer"
import { FallbackNote } from "../../components/FallbackNote"
import type { ActionPlan, ActionResult, DataSource } from "../../types/api"
import { SyntheticStateView } from "./SyntheticStateView"

type Phase = "planning" | "review" | "executing" | "complete"

const PHASES: { id: Phase; label: string }[] = [
  { id: "planning", label: "Planning" },
  { id: "review", label: "Review" },
  { id: "executing", label: "Executing" },
  { id: "complete", label: "Complete" },
]

export function TakeActionDrawer({
  caseId,
  onClose,
}: {
  caseId: string
  onClose: () => void
}) {
  const [phase, setPhase] = useState<Phase>("planning")
  const [plan, setPlan] = useState<ActionPlan | null>(null)
  const [planSource, setPlanSource] = useState<DataSource>("api")
  const [result, setResult] = useState<ActionResult | null>(null)
  const [resultSource, setResultSource] = useState<DataSource>("api")
  const [reviewed, setReviewed] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let active = true
    const started = Date.now()

    loadPlan(caseId)
      .then(async (loaded) => {
        const wait = Math.max(0, 350 - (Date.now() - started))
        if (wait > 0) {
          await delay(wait)
        }
        if (!active) {
          return
        }
        setPlan(loaded.plan)
        setPlanSource(loaded.source)
        setPhase("review")
      })
      .catch((loadError: unknown) => {
        if (!active) {
          return
        }
        setError(errorMessage(loadError))
        setPhase("review")
      })

    return () => {
      active = false
    }
  }, [attempt, caseId])

  async function approve() {
    if (!plan || !reviewed || phase === "executing") {
      return
    }
    setPhase("executing")
    setError(null)
    const started = Date.now()
    try {
      const executed = await runPlan(plan, planSource)
      const wait = Math.max(0, 450 - (Date.now() - started))
      if (wait > 0) {
        await delay(wait)
      }
      setResult(executed.result)
      setResultSource(executed.source)
      setPhase("complete")
    } catch (executeError) {
      setError(errorMessage(executeError))
      setPhase("review")
    }
  }

  const phaseIndex = PHASES.findIndex((item) => item.id === phase)

  return (
    <Drawer title="TAKE ACTION" onClose={onClose}>
      <ol className="stepper" aria-label="Action progress">
        {PHASES.map((item, index) => (
          <li key={item.id} className={index <= phaseIndex ? "reached" : ""}>
            {item.label}
          </li>
        ))}
      </ol>

      {phase === "planning" ? (
        <p className="status-copy" role="status">
          Planning
        </p>
      ) : null}

      {error ? (
        <div className="drawer-error" role="alert">
          <p>{error}</p>
          {!plan ? (
            <button
              type="button"
              className="open-button"
              onClick={() => {
                setPhase("planning")
                setPlan(null)
                setResult(null)
                setReviewed(false)
                setError(null)
                setAttempt((current) => current + 1)
              }}
            >
              Try again
            </button>
          ) : null}
        </div>
      ) : null}

      {plan ? (
        <>
          <FallbackNote
            source={planSource}
            text="Local fallback. The decision service did not return this plan."
          />
          <p className="mono plan-id">{plan.plan_id}</p>
          <ol className="plan-steps">
            {plan.steps.map((step) => (
              <li key={`${step.tool}-${step.summary}`}>
                <p className="tool">{step.tool}</p>
                <p>{step.summary}</p>
                <dl>
                  {Object.entries(step.args).map(([key, value]) => (
                    <div key={key}>
                      <dt>{key}</dt>
                      <dd>{value}</dd>
                    </div>
                  ))}
                </dl>
              </li>
            ))}
          </ol>
          <SyntheticStateView title="BEFORE" state={plan.before_state} />
        </>
      ) : null}

      {plan && !plan.requires_approval && phase !== "planning" ? (
        <p className="policy-note">
          Applied under policy. This plan did not require approval, so the service
          applied it when the plan was created. An after-state is returned only by
          execution.
        </p>
      ) : null}

      {plan?.requires_approval && phase !== "complete" ? (
        <div className="approval">
          <label>
            <input
              type="checkbox"
              checked={reviewed}
              onChange={(event) => setReviewed(event.target.checked)}
              disabled={phase === "executing"}
            />
            I have reviewed this plan
          </label>
          <button
            type="button"
            className="approve-button"
            disabled={!reviewed || phase === "executing" || phase === "planning"}
            onClick={() => void approve()}
          >
            APPROVE & EXECUTE
          </button>
        </div>
      ) : null}

      {phase === "executing" ? (
        <p className="status-copy" role="status">
          Executing
        </p>
      ) : null}

      {phase === "complete" && result ? (
        <div className="complete">
          <p className="complete-mark">Complete · {result.status}</p>
          <FallbackNote
            source={resultSource}
            text="Local fallback. The service did not execute this plan."
          />
          <ul className="result-list">
            {result.results.map((item) => (
              <li key={`${item.tool}-${item.summary}`}>
                <span className="tool">{item.tool}</span>
                {item.summary}
              </li>
            ))}
          </ul>
          <SyntheticStateView title="AFTER" state={result.after_state} />
        </div>
      ) : null}

      <button type="button" className="cancel-button" onClick={onClose}>
        CANCEL
      </button>
    </Drawer>
  )
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

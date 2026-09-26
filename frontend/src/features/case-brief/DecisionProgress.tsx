export function DecisionProgress({
  account,
  claim,
  steps,
  step,
}: {
  account: string
  claim: string
  steps: string[]
  step: number
}) {
  return (
    <section className="progress" aria-live="polite">
      <p className="eyebrow">DECISION AGENT</p>
      {account ? (
        <p className="progress-case">
          {account}
          {claim ? ` · ${claim}` : ""}
        </p>
      ) : null}
      <ol>
        {steps.map((label, index) => {
          const state = index < step ? "done" : index === step ? "current" : "waiting"
          return (
            <li key={label} className={state}>
              <span aria-hidden="true">{state === "waiting" ? "·" : "→"}</span>
              {label}
            </li>
          )
        })}
      </ol>
    </section>
  )
}

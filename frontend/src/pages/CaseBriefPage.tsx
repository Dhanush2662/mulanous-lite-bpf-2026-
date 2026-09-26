import { useState } from "react"
import { Link, useLocation, useParams } from "react-router-dom"

import { AppHeader } from "../components/AppHeader"
import { FallbackNote } from "../components/FallbackNote"
import { CaseBriefView } from "../features/case-brief/CaseBriefView"
import { DecisionProgress } from "../features/case-brief/DecisionProgress"
import { EvidenceInspector } from "../features/case-brief/EvidenceInspector"
import { TakeActionDrawer } from "../features/case-brief/TakeActionDrawer"
import { useCaseAnalysis } from "../hooks/useCaseAnalysis"
import type { Case, EvidenceRecord } from "../types/api"

export function CaseBriefPage() {
  const { caseId = "" } = useParams()
  const location = useLocation()
  const preview = readPreview(location.state)
  const [inspected, setInspected] = useState<EvidenceRecord | null>(null)
  const [planning, setPlanning] = useState(false)
  const analysisState = useCaseAnalysis(caseId, preview)

  const account = analysisState.analysis?.account ?? preview?.account ?? ""
  const claim = analysisState.analysis?.claim ?? preview?.claim ?? ""
  const evidence = analysisState.analysis?.evidence ?? []
  const selected = evidence.find((record) => record.id === inspected?.id) ?? evidence[0] ?? null

  return (
    <>
      <AppHeader />
      <main className="page">
        <Link to="/" className="back-link">
          Back to Attention Today
        </Link>

        {analysisState.phase === "progress" ? (
          <DecisionProgress
            account={account}
            claim={claim}
            steps={analysisState.steps}
            step={analysisState.step}
          />
        ) : null}

        {analysisState.phase === "error" ? (
          <div className="status-panel" role="alert">
            <p>Analysis did not complete.</p>
            <p>{analysisState.error}</p>
            <button type="button" className="open-button" onClick={analysisState.retry}>
              Try again
            </button>
          </div>
        ) : null}

        {analysisState.phase === "ready" && analysisState.analysis ? (
          <>
            <FallbackNote
              source={analysisState.source}
              text="Local fallback. The decision service did not return this analysis."
            />
            <div className="brief-layout">
              <CaseBriefView
                analysis={analysisState.analysis}
                domain={analysisState.domain}
                selectedId={selected?.id ?? null}
                onInspect={setInspected}
                onPlan={() => setPlanning(true)}
              />
              <EvidenceInspector record={selected} />
            </div>
          </>
        ) : null}
      </main>
      {planning ? (
        <TakeActionDrawer caseId={caseId} onClose={() => setPlanning(false)} />
      ) : null}
    </>
  )
}

function readPreview(state: unknown): Case | null {
  if (!state || typeof state !== "object" || !("preview" in state)) {
    return null
  }
  const preview = (state as { preview?: Case }).preview
  if (!preview || typeof preview.id !== "string") {
    return null
  }
  return preview
}

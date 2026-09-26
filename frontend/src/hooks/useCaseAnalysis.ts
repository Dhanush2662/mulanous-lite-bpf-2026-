import { useEffect, useState } from "react"

import { errorMessage, loadAnalysis } from "../api/client"
import { FALLBACK_CASES } from "../api/fallback"
import { progressSteps } from "../features/labels"
import type { AnalyzeResponse, Case, DataSource, Domain } from "../types/api"

const STEP_MS = 280

export function useCaseAnalysis(caseId: string, preview: Case | null) {
  const [attempt, setAttempt] = useState(0)
  const [phase, setPhase] = useState<"progress" | "ready" | "error">("progress")
  const [step, setStep] = useState(0)
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null)
  const [source, setSource] = useState<DataSource>("api")
  const [error, setError] = useState<string | null>(null)
  const domain = domainFor(caseId, preview)
  const steps = progressSteps(domain)

  useEffect(() => {
    let active = true
    const started = Date.now()
    const timer = window.setInterval(() => {
      setStep((current) => Math.min(current + 1, steps.length - 1))
    }, STEP_MS)

    loadAnalysis(caseId)
      .then(async (result) => {
        const wait = Math.max(0, STEP_MS * steps.length - (Date.now() - started))
        if (wait > 0) {
          await delay(wait)
        }
        if (!active) {
          return
        }
        window.clearInterval(timer)
        setStep(steps.length - 1)
        setAnalysis(result.analysis)
        setSource(result.source)
        setPhase("ready")
      })
      .catch((loadError: unknown) => {
        if (!active) {
          return
        }
        window.clearInterval(timer)
        setError(errorMessage(loadError))
        setPhase("error")
      })

    return () => {
      active = false
      window.clearInterval(timer)
    }
  }, [attempt, caseId, domain, steps.length])

  return {
    phase,
    step,
    steps,
    analysis,
    source,
    error,
    domain,
    retry: () => {
      setPhase("progress")
      setStep(0)
      setAnalysis(null)
      setError(null)
      setAttempt((current) => current + 1)
    },
  }
}

function domainFor(caseId: string, preview: Case | null): Domain {
  if (preview?.domain) {
    return preview.domain
  }
  return FALLBACK_CASES.find((item) => item.id === caseId)?.domain ?? "software"
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

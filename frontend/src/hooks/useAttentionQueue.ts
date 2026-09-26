import { useEffect, useState } from "react"

import { loadCases } from "../api/client"
import type { Case, DataSource } from "../types/api"

export function useAttentionQueue() {
  const [attempt, setAttempt] = useState(0)
  const [loading, setLoading] = useState(true)
  const [cases, setCases] = useState<Case[]>([])
  const [source, setSource] = useState<DataSource>("api")

  useEffect(() => {
    let active = true
    loadCases().then((result) => {
      if (!active) {
        return
      }
      setCases(result.cases)
      setSource(result.source)
      setLoading(false)
    })
    return () => {
      active = false
    }
  }, [attempt])

  return {
    cases,
    source,
    loading,
    reload: () => {
      setLoading(true)
      setAttempt((current) => current + 1)
    },
  }
}

import { useCallback, useEffect, useRef, useState } from 'react'
import type {
  ArenaCompareResponse,
  ArenaModelConfig,
  ArenaRun,
  BatchTrainResponse,
} from '../types/arena'
import * as arenaApi from '../api/arena'

export function useArena(sessionId: string | null) {
  const [runs, setRuns] = useState<ArenaRun[]>([])
  const [comparison, setComparison] = useState<ArenaCompareResponse | null>(null)
  const [isTraining, setIsTraining] = useState(false)
  const [isComparing, setIsComparing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Abort in-flight requests on unmount
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    return () => {
      abortRef.current?.abort()
    }
  }, [])

  const fetchRuns = useCallback(async () => {
    if (!sessionId) return
    try {
      const data = await arenaApi.getArenaRuns(sessionId)
      setRuns(data)
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') return
      setError(e instanceof Error ? e.message : 'Failed to fetch runs')
    }
  }, [sessionId])

  const batchTrain = useCallback(
    async (models: ArenaModelConfig[]): Promise<BatchTrainResponse | null> => {
      if (!sessionId) return null
      abortRef.current?.abort()
      const controller = new AbortController()
      abortRef.current = controller
      setIsTraining(true)
      setError(null)
      try {
        const result = await arenaApi.batchTrain(
          { session_id: sessionId, models },
          controller.signal,
        )
        setRuns((prev) => {
          const existingIds = new Set(prev.map((r) => r.run_id))
          const newRuns = result.runs.filter((r) => !existingIds.has(r.run_id))
          return [...prev, ...newRuns]
        })
        return result
      } catch (e) {
        if (e instanceof DOMException && e.name === 'AbortError') return null
        setError(e instanceof Error ? e.message : 'Batch training failed')
        return null
      } finally {
        setIsTraining(false)
      }
    },
    [sessionId]
  )

  const compareSelected = useCallback(
    async (runIds: string[]) => {
      if (!sessionId) return
      setIsComparing(true)
      setError(null)
      try {
        const result = await arenaApi.compareRuns(sessionId, runIds)
        setComparison(result)
      } catch (e) {
        if (e instanceof DOMException && e.name === 'AbortError') return
        setError(e instanceof Error ? e.message : 'Comparison failed')
      } finally {
        setIsComparing(false)
      }
    },
    [sessionId]
  )

  const clearRuns = useCallback(async () => {
    if (!sessionId) return
    try {
      await arenaApi.clearArenaRuns(sessionId)
      setRuns([])
      setComparison(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to clear runs')
    }
  }, [sessionId])

  return {
    runs,
    comparison,
    isTraining,
    isComparing,
    error,
    fetchRuns,
    batchTrain,
    compareSelected,
    clearRuns,
  }
}

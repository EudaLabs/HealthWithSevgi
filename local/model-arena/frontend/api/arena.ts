import { api } from '../../../../frontend/src/api/client'
import type {
  ArenaCompareResponse,
  ArenaRun,
  BatchTrainRequest,
  BatchTrainResponse,
} from '../types/arena'

export const batchTrain = (
  req: BatchTrainRequest,
  signal?: AbortSignal,
): Promise<BatchTrainResponse> =>
  api.post<BatchTrainResponse>('/arena/batch-train', req, { signal }).then((r) => r.data)

export const getArenaRuns = (sessionId: string): Promise<ArenaRun[]> =>
  api.get<ArenaRun[]>(`/arena/runs/${sessionId}`).then((r) => r.data)

export const compareRuns = (
  sessionId: string,
  runIds: string[]
): Promise<ArenaCompareResponse> =>
  api
    .post<ArenaCompareResponse>(`/arena/compare/${sessionId}`, { run_ids: runIds })
    .then((r) => r.data)

export const clearArenaRuns = (sessionId: string): Promise<void> =>
  api.delete(`/arena/runs/${sessionId}`).then(() => undefined)

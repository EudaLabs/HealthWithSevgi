import { api } from './client'
import type { CompareEntry, ModelType, TrainResponse } from '../types'

export const trainModel = (
  sessionId: string,
  modelType: ModelType,
  params: Record<string, unknown>,
  options?: { tune?: boolean; useFeatureSelection?: boolean; signal?: AbortSignal }
): Promise<TrainResponse> =>
  api
    .post<TrainResponse>(
      '/train',
      {
        session_id: sessionId,
        model_type: modelType,
        params,
        tune: options?.tune,
        use_feature_selection: options?.useFeatureSelection,
      },
      { signal: options?.signal }
    )
    .then((r) => r.data)

export const addToComparison = (modelId: string): Promise<{ entries: CompareEntry[]; best_model_id: string }> =>
  api.post(`/compare/${modelId}`).then((r) => r.data)

export const getComparison = (sessionId: string): Promise<{ entries: CompareEntry[]; best_model_id: string }> =>
  api.get(`/compare/${sessionId}`).then((r) => r.data)

export const clearComparison = (sessionId: string): Promise<void> =>
  api.delete(`/compare/${sessionId}`).then(() => undefined)

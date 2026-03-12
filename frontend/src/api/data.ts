import { api } from './client'
import type { DataExplorationResponse, PrepResponse } from '../types'

export const exploreData = (
  specialtyId: string,
  targetCol: string,
  file?: File | null
): Promise<DataExplorationResponse> => {
  const fd = new FormData()
  fd.append('specialty_id', specialtyId)
  fd.append('target_col', targetCol)
  if (file) fd.append('file', file)
  return api.post<DataExplorationResponse>('/explore', fd).then((r) => r.data)
}

export const prepareData = (params: {
  specialtyId: string
  targetCol: string
  testSize: number
  missingStrategy: string
  normalization: string
  useSmote: boolean
  sessionId?: string
  file?: File | null
}): Promise<PrepResponse> => {
  const fd = new FormData()
  fd.append('specialty_id', params.specialtyId)
  fd.append('target_col', params.targetCol)
  fd.append('test_size', String(params.testSize))
  fd.append('missing_strategy', params.missingStrategy)
  fd.append('normalization', params.normalization)
  fd.append('use_smote', String(params.useSmote))
  if (params.sessionId) fd.append('session_id', params.sessionId)
  if (params.file) fd.append('file', params.file)
  return api.post<PrepResponse>('/prepare', fd).then((r) => r.data)
}

import { api } from './client'
import type { DataExplorationResponse, PrepResponse } from '../types'

/**
 * Step 2 — Data Exploration.
 * Sends the chosen specialty (and optionally an uploaded CSV) to the backend,
 * which returns column summaries, missing-value counts, class balance, and
 * suggested preprocessing hints for the Column Mapper UI.
 *
 * @param specialtyId  Specialty registry id (e.g. `"endocrinology_diabetes"`).
 * @param targetCol    Column the user chose as the prediction target.
 * @param file         Optional override CSV; when omitted, the backend uses
 *                     the bundled sample dataset for that specialty.
 */
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

/**
 * Step 3 — Data Preparation.
 * Triggers the train/test split, missing-value imputation, normalization,
 * optional SMOTE oversampling, and outlier handling. The returned
 * `PrepResponse.session_id` is the key every downstream call (train, SHAP,
 * ethics, certificate) uses to retrieve this dataset from the backend LRU.
 */
export const prepareData = (params: {
  specialtyId: string
  targetCol: string
  testSize: number
  missingStrategy: string
  normalization: string
  useSmote: boolean
  outlierHandling: string
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
  fd.append('outlier_handling', params.outlierHandling)
  if (params.sessionId) fd.append('session_id', params.sessionId)
  if (params.file) fd.append('file', params.file)
  return api.post<PrepResponse>('/prepare', fd).then((r) => r.data)
}

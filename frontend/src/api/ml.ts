import { api } from './client'
import type { CompareEntry, ModelType, TrainResponse } from '../types'

/**
 * Step 4 — Model training.
 * Trains one of the 8 supported classifiers against the prepared session,
 * returning metrics, ROC/PR curves, confusion matrix, and a model id used
 * for explainability and comparison.
 *
 * @param sessionId  Session id from `prepareData`.
 * @param modelType  One of knn | svm | decision_tree | random_forest |
 *                   logistic_regression | naive_bayes | xgboost | lightgbm.
 * @param params     Model-specific hyperparameters (matches the sliders on
 *                   Step 4). Unknown keys are ignored by the backend.
 * @param options.tune              When `true`, the backend runs grid search
 *                                  and returns the best-found params.
 * @param options.useFeatureSelection  When `true`, drops low-importance
 *                                  columns before fitting.
 * @param options.signal            AbortSignal to cancel long-running trains
 *                                  when the user navigates away.
 */
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

/** Add the given trained model to the session's side-by-side comparison set. */
export const addToComparison = (modelId: string): Promise<{ entries: CompareEntry[]; best_model_id: string }> =>
  api.post(`/compare/${modelId}`).then((r) => r.data)

/** Read all models currently in the session's comparison set. */
export const getComparison = (sessionId: string): Promise<{ entries: CompareEntry[]; best_model_id: string }> =>
  api.get(`/compare/${sessionId}`).then((r) => r.data)

/** Empty the comparison set — used by the "Clear all" control in Step 5. */
export const clearComparison = (sessionId: string): Promise<void> =>
  api.delete(`/compare/${sessionId}`).then(() => undefined)

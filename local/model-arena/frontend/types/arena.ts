import type { KNNScatterData, MetricsResponse, ModelType } from '../../../../frontend/src/types'

/**
 * Safely extract a numeric metric value from MetricsResponse.
 * Components using this only receive completed runs (metrics is non-null),
 * but TypeScript cannot infer that from the filter.
 */
export function getMetric(metrics: MetricsResponse | null, key: string): number {
  if (!metrics) return 0
  return (metrics as unknown as Record<string, number>)[key] ?? 0
}

export interface ArenaModelConfig {
  model_type: ModelType
  params: Record<string, unknown>
  tune?: boolean
  use_feature_selection?: boolean
}

export interface BatchTrainRequest {
  session_id: string
  models: ArenaModelConfig[]
}

export interface ArenaRun {
  run_id: string
  model_id: string
  model_type: ModelType
  params: Record<string, unknown>
  metrics: MetricsResponse | null  // null for failed runs
  training_time_ms: number
  feature_names: string[]
  knn_scatter?: KNNScatterData
  status: 'completed' | 'failed'
  error?: string
}

export interface BatchTrainResponse {
  session_id: string
  runs: ArenaRun[]
  total_training_time_ms: number
  best_run_id: string | null
}

export interface ArenaCompareResponse {
  runs: ArenaRun[]
  best_run_id: string | null
  metric_summary: Record<string, Record<string, number>>
  param_diff: Record<string, Record<string, unknown>>
}

/** Labels for display */
export const MODEL_LABELS: Record<ModelType, string> = {
  knn: 'KNN',
  svm: 'SVM',
  decision_tree: 'Decision Tree',
  random_forest: 'Random Forest',
  logistic_regression: 'Logistic Regression',
  naive_bayes: 'Naive Bayes',
  xgboost: 'XGBoost',
  lightgbm: 'LightGBM',
}

export const METRIC_LABELS: Record<string, string> = {
  accuracy: 'Accuracy',
  sensitivity: 'Sensitivity',
  specificity: 'Specificity',
  precision: 'Precision',
  f1_score: 'F1 Score',
  auc_roc: 'AUC-ROC',
  mcc: 'MCC',
  train_accuracy: 'Train Accuracy',
  training_time_ms: 'Training Time (ms)',
}

/** Color palette for up to 8 models */
export const RUN_COLORS = [
  '#6366f1', '#f43f5e', '#10b981', '#f59e0b',
  '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6',
]

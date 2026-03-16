export interface Specialty {
  id: string
  name: string
  description: string
  target_variable: string
  target_type: 'binary' | 'multiclass'
  feature_names: string[]
  clinical_context: string
  data_source: string
  what_ai_predicts: string
}

export interface ColumnStat {
  name: string
  dtype: string
  missing_count: number
  missing_pct: number
  unique_count: number
  sample_values: (string | number | boolean | null)[]
}

export interface DataExplorationResponse {
  columns: ColumnStat[]
  row_count: number
  class_distribution: Record<string, number>
  imbalance_warning: boolean
  imbalance_ratio: number
  target_col: string
}

export type MissingStrategy = 'median' | 'mode' | 'drop'
export type Normalization = 'zscore' | 'minmax' | 'none'

export interface PrepSettings {
  test_size: number
  missing_strategy: MissingStrategy
  normalization: Normalization
  use_smote: boolean
}

export interface PrepResponse {
  session_id: string
  train_size: number
  test_size: number
  features_count: number
  class_distribution_before: Record<string, number>
  class_distribution_after: Record<string, number>
  smote_applied: boolean
  normalization_applied: string
  norm_samples: { feature: string; before: number; after: number }[]
}

export type ModelType =
  | 'knn'
  | 'svm'
  | 'decision_tree'
  | 'random_forest'
  | 'logistic_regression'
  | 'naive_bayes'
  | 'xgboost'
  | 'lightgbm'

export interface ConfusionMatrixData {
  tn: number
  fp: number
  fn: number
  tp: number
  matrix: number[][]
  labels: string[]
}

export interface ROCPoint {
  fpr: number
  tpr: number
  threshold: number
}

export interface MetricsResponse {
  accuracy: number
  sensitivity: number
  specificity: number
  precision: number
  f1_score: number
  auc_roc: number
  confusion_matrix: ConfusionMatrixData
  roc_curve: ROCPoint[]
  pr_curve: { precision: number; recall: number }[]
  train_accuracy: number
  cross_val_scores: number[]
  low_sensitivity_warning: boolean
  mcc: number
  overfitting_warning: boolean
}

export interface TrainResponse {
  model_id: string
  session_id: string
  model_type: ModelType
  params: Record<string, unknown>
  metrics: MetricsResponse
  training_time_ms: number
  feature_names: string[]
}

export interface CompareEntry {
  model_id: string
  model_type: ModelType
  params: Record<string, unknown>
  metrics: MetricsResponse
  training_time_ms: number
}

export interface FeatureImportanceItem {
  feature_name: string
  clinical_name: string
  importance: number
  direction: 'positive' | 'negative' | 'neutral'
  clinical_note: string
}

export interface GlobalExplainabilityResponse {
  model_id: string
  method: string
  feature_importances: FeatureImportanceItem[]
  top_feature_clinical_note: string
  explained_variance_pct: number
}

export interface SHAPWaterfallPoint {
  feature_name: string
  clinical_name: string
  feature_value: number | string
  shap_value: number
  direction: 'increases_risk' | 'decreases_risk'
  plain_language: string
}

export interface SinglePatientExplainResponse {
  model_id: string
  patient_index: number
  predicted_class: string
  predicted_probability: number
  base_value: number
  waterfall: SHAPWaterfallPoint[]
  clinical_summary: string
}

export interface SubgroupMetrics {
  group_name: string
  group_label: string
  sample_size: number
  accuracy: number
  sensitivity: number
  specificity: number
  precision: number
  f1_score: number
  status: 'acceptable' | 'review' | 'action_needed'
}

export interface BiasWarning {
  detected: boolean
  message: string
  affected_group: string
  metric: string
  gap: number
}

export interface EthicsResponse {
  model_id: string
  subgroup_metrics: SubgroupMetrics[]
  bias_warnings: BiasWarning[]
  training_representation: {
    gender: { dataset: Record<string, number>; population_norm: Record<string, number> }
    age_group: { dataset: Record<string, number>; population_norm: Record<string, number> }
  }
  overall_sensitivity: number
  eu_ai_act_items: {
    id: string
    text: string
    pre_checked: boolean
    checked?: boolean
  }[]
  case_studies: {
    id: string
    title: string
    specialty: string
    year: number
    what_happened: string
    impact: string
    lesson: string
  }[]
}

export interface WizardState {
  specialty: Specialty | null
  explorationData: DataExplorationResponse | null
  targetColumn: string | null
  uploadedFile: File | null
  prepResponse: PrepResponse | null
  prepSettings: PrepSettings
  trainResponse: TrainResponse | null
  comparedModels: CompareEntry[]
  stepsCompleted: Set<number>
  currentStep: number
}

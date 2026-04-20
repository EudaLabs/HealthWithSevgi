import { api } from './client'
import type { EthicsResponse, GlobalExplainabilityResponse, SinglePatientExplainResponse, WhatIfResponse, SamplePatientsResponse } from '../types'

/**
 * Step 6 — Global feature importance.
 * Returns the SHAP-derived ranking of which features drove the model overall,
 * along with clinical display names for each raw column.
 */
export const fetchGlobalExplainability = (modelId: string): Promise<GlobalExplainabilityResponse> =>
  api.get<GlobalExplainabilityResponse>(`/explain/global/${modelId}`).then((r) => r.data)

/**
 * Step 6 — Per-patient waterfall.
 * SHAP values for a single test-set patient so the UI can render
 * "why did the model predict X for this patient".
 */
export const fetchPatientExplanation = (
  modelId: string,
  patientIndex: number
): Promise<SinglePatientExplainResponse> =>
  api.get<SinglePatientExplainResponse>(`/explain/patient/${modelId}/${patientIndex}`).then((r) => r.data)

/**
 * Step 7 — Fairness / ethics audit.
 * Subgroup performance (by sex / age / etc.), bias flags, the EU AI Act
 * checklist, documented case studies, and training-set representation stats.
 */
export const fetchEthics = (modelId: string): Promise<EthicsResponse> =>
  api.get<EthicsResponse>(`/ethics/${modelId}`).then((r) => r.data)

/**
 * Step 6 — Patient dropdown source.
 * The backend pre-selects 3 representative test-set patients (low / mid /
 * high predicted probability) so the demo has a meaningful default trio.
 */
export const fetchSamplePatients = (modelId: string): Promise<SamplePatientsResponse> =>
  api.get<SamplePatientsResponse>(`/explain/sample-patients/${modelId}`).then((r) => r.data)

/**
 * Step 6 — What-if simulator.
 * Re-runs the model with a single feature value overridden for the chosen
 * patient, returning the original vs new probability shift. Used by the
 * blue what-if banner.
 */
export const fetchWhatIf = (payload: {
  model_id: string
  patient_index: number
  feature_name: string
  new_value: number
}): Promise<WhatIfResponse> =>
  api.post<WhatIfResponse>('/explain/what-if', payload).then((r) => r.data)

/** Single EU AI Act item after LLM enrichment (see `InsightResponse`). */
export interface EuAiActEnrichedItem {
  id: string
  enriched_description: string
}

/**
 * Step 7 — AI-authored narrative bundle.
 * The backend calls an LLM once per model and returns plain-text narratives
 * for the ethics summary, case-study framing, and per-item EU AI Act
 * guidance. Cached server-side so repeat calls are free.
 */
export interface InsightResponse {
  ethics_insight: { source: string; text: string }
  case_studies: { source: string; text: string; case_studies?: CaseStudyData[] }
  eu_ai_act_insights?: { source: string; text: string; items?: EuAiActEnrichedItem[] }
}

/**
 * Step 7 — Documented real-world case study.
 * `severity` drives the card border colour: failure=red, near_miss=amber,
 * prevention=green.
 */
export interface CaseStudyData {
  title: string
  specialty: string
  year: number
  severity: 'failure' | 'near_miss' | 'prevention'
  what_happened: string
  impact: string
  lesson: string
}

/** Fetch the Step 7 narrative bundle (see `InsightResponse`). */
export const fetchInsights = (modelId: string): Promise<InsightResponse> =>
  api.get<InsightResponse>(`/insights/${modelId}`).then((r) => r.data)

/**
 * Step 7 — Persist a single EU AI Act checklist toggle.
 * Fire-and-forget: the Step 7 UI updates local state optimistically and
 * only surfaces errors via a toast.
 */
export const updateChecklist = (modelId: string, itemId: string, checked: boolean): Promise<void> =>
  api.post('/ethics/checklist', { model_id: modelId, item_id: itemId, checked }).then(() => undefined)

/**
 * Step 7 — Generate + download the final compliance PDF certificate.
 *
 * Posts the checklist state plus clinician/institution metadata, receives
 * the ReportLab-generated PDF as a blob, and triggers a browser download
 * named `ml_certificate_<first-8-chars-of-model-id>.pdf`.
 */
export const downloadCertificate = async (payload: {
  model_id: string
  session_id: string
  checklist_state: Record<string, boolean>
  clinician_name: string
  institution: string
}): Promise<void> => {
  const response = await api.post('/generate-certificate', payload, { responseType: 'blob' })
  const blob = new Blob([response.data as BlobPart], { type: 'application/pdf' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ml_certificate_${payload.model_id.slice(0, 8)}.pdf`
  a.click()
  URL.revokeObjectURL(url)
}

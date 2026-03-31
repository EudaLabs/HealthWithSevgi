import { api } from './client'
import type { EthicsResponse, GlobalExplainabilityResponse, SinglePatientExplainResponse } from '../types'

export const fetchGlobalExplainability = (modelId: string): Promise<GlobalExplainabilityResponse> =>
  api.get<GlobalExplainabilityResponse>(`/explain/global/${modelId}`).then((r) => r.data)

export const fetchPatientExplanation = (
  modelId: string,
  patientIndex: number
): Promise<SinglePatientExplainResponse> =>
  api.get<SinglePatientExplainResponse>(`/explain/patient/${modelId}/${patientIndex}`).then((r) => r.data)

export const fetchEthics = (modelId: string): Promise<EthicsResponse> =>
  api.get<EthicsResponse>(`/ethics/${modelId}`).then((r) => r.data)

export const updateChecklist = (modelId: string, itemId: string, checked: boolean): Promise<void> =>
  api.post('/ethics/checklist', { model_id: modelId, item_id: itemId, checked }).then(() => undefined)

export const downloadCertificate = async (payload: {
  model_id: string
  session_id: string
  checklist_state: Record<string, boolean>
  clinician_name: string
  institution: string
}): Promise<void> => {
  const response = await api.post('/certificate', payload, { responseType: 'blob' })
  const blob = new Blob([response.data as BlobPart], { type: 'application/pdf' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ml_certificate_${payload.model_id.slice(0, 8)}.pdf`
  a.click()
  URL.revokeObjectURL(url)
}

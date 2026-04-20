import { api } from './client'
import type { Specialty } from '../types'

/**
 * List every medical specialty registered in the backend.
 * Used by Step 1 (Clinical Context) to populate the domain pill bar —
 * the returned order drives the on-screen order.
 */
export const fetchSpecialties = (): Promise<Specialty[]> =>
  api.get<Specialty[]>('/specialties').then((r) => r.data)

/**
 * Fetch a single specialty's full config (dataset path, clinical names,
 * default target column, description). Called when the user picks a pill
 * so Step 1 can render the specialty-specific intro copy.
 */
export const fetchSpecialty = (id: string): Promise<Specialty> =>
  api.get<Specialty>(`/specialties/${id}`).then((r) => r.data)

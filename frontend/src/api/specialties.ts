import { api } from './client'
import type { Specialty } from '../types'

export const fetchSpecialties = (): Promise<Specialty[]> =>
  api.get<Specialty[]>('/specialties').then((r) => r.data)

export const fetchSpecialty = (id: string): Promise<Specialty> =>
  api.get<Specialty>(`/specialties/${id}`).then((r) => r.data)

// Common types for the application

export enum UserRole {
  ADMIN = 'ADMIN',
  SUP = 'SUP',
  OPER = 'OPER',
}

export interface User {
  id: number
  nombre: string
  email: string
  rol: UserRole
  activo: boolean
  created_at: string
}

export interface Bus {
  id: number
  ppu: string
  alias?: string
  activo: boolean
  created_at: string
}

export enum CleaningState {
  CLEAN = 'clean',
  DIRTY = 'dirty',
  UNCERTAIN = 'uncertain',
}

export interface CleaningEvent {
  id: number
  bus_id: number
  user_id: number
  estado: CleaningState
  confidence?: number
  observaciones?: string
  imagen_thumb_url?: string
  origen: 'edge' | 'server' | 'manual'
  issues?: {
    issues?: string[]
    suggestions?: string[]
  }
  created_at: string
  bus_ppu?: string
  user_nombre?: string
}

export interface Alert {
  id: number
  bus_id: number
  tipo: 'repetido' | 'muy_sucio' | 'dudoso_recurrente'
  nivel: 'info' | 'warn' | 'critical'
  detalle: string
  created_at: string
  resolved_by?: number
  resolved_at?: string
  bus_ppu?: string
}

export interface AnalysisResponse {
  estado: CleaningState
  confidence: number
  issues: string[]
  suggestions: string[]
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

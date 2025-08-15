import axios from 'axios'
export const api = axios.create({ baseURL: '/api' })

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export type PropLeg = {
  player_id: number
  prop: 'pts' | 'reb' | 'ast' | 'stl' | 'blk' | 'tov' | 'fg3m'
  threshold: number
  op?: '>=' | '>' | 'over'
  date?: string | null
}
export type Player = {
  id: number
  full_name: string
  team_abbrev?: string | null
}
export type IngestTask = {
  id: string
  status: 'queued' | 'running' | 'done' | 'error'
  message: string
  progress: number
  result_rows: number
}

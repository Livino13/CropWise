import type { SoilInput, RecommendationResult, Field, WeatherData, AnalyticsData, HistoryEntry, Feedback, ModelStatus, GuidanceResult, ChatMessage, ChatReply, PlanOptions, CropPlan } from './types'

const base = (import.meta as unknown as { env?: Record<string,string> }).env?.VITE_API_URL || ''

async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const r = await fetch(`${base}${path}`, { headers: { 'Content-Type': 'application/json' }, ...opts })
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`)
  if (r.status === 204) return undefined as T
  return r.json() as Promise<T>
}

export function recommend(data: SoilInput): Promise<RecommendationResult> {
  return req<RecommendationResult>('/api/recommend', { method: 'POST', body: JSON.stringify(data) })
}
export function getWeather(lat: number, lon: number): Promise<WeatherData> {
  return req<WeatherData>('/api/weather', { method: 'POST', body: JSON.stringify({ latitude: lat, longitude: lon }) })
}
export function getAnalytics(): Promise<AnalyticsData> {
  return req<AnalyticsData>('/api/analytics')
}
export function getFields(): Promise<Field[]> {
  return req<Field[]>('/api/fields')
}
export function createField(d: Partial<Field>): Promise<Field> {
  return req<Field>('/api/fields', { method: 'POST', body: JSON.stringify(d) })
}
export function updateField(id: number, d: Partial<Field>): Promise<Field> {
  return req<Field>(`/api/fields/${id}`, { method: 'PUT', body: JSON.stringify(d) })
}
export function deleteField(id: number): Promise<void> {
  return req<void>(`/api/fields/${id}`, { method: 'DELETE' })
}
export function getHistory(params: Record<string,string> = {}): Promise<HistoryEntry[]> {
  const qs = new URLSearchParams({ limit: '500', ...params }).toString()
  return req<HistoryEntry[] | { items: HistoryEntry[] }>(`/api/history${qs ? `?${qs}` : ''}`).then((r: unknown) => Array.isArray(r) ? r as HistoryEntry[] : (r as { items: HistoryEntry[] }).items)
}
export function setRecommendationField(id: number, fieldId: number | null): Promise<{ id: number; field_id: number | null }> {
  return req<{ id: number; field_id: number | null }>(`/api/history/${id}`, { method: 'PATCH', body: JSON.stringify({ field_id: fieldId }) })
}
export function submitFeedback(data: Feedback): Promise<{ id: number; message: string }> {
  return req<{ id: number; message: string }>('/api/feedback', { method: 'POST', body: JSON.stringify(data) })
}
export function retrainModel(): Promise<{ status: string }> {
  return req<{ status: string }>('/api/model/retrain', { method: 'POST' })
}
export function getModelStatus(): Promise<ModelStatus> {
  return req<ModelStatus>('/api/model/status')
}
export function getGuidance(crop: string, opts: { soil_type?: string; field_id?: number } = {}): Promise<GuidanceResult> {
  return req<GuidanceResult>('/api/guidance', { method: 'POST', body: JSON.stringify({ crop, ...opts }) })
}
export function getPlan(crop: string, opts: PlanOptions = {}): Promise<CropPlan> {
  return req<CropPlan>('/api/plan', { method: 'POST', body: JSON.stringify({ crop, ...opts }) })
}
export function sendChat(messages: ChatMessage[], context?: string): Promise<ChatReply> {
  return req<ChatReply>('/api/chat', { method: 'POST', body: JSON.stringify({ messages: messages.slice(-10), context }) })
}

// Backwards-compat object — existing pages import `api.weather` etc.
export const api = {
  recommend, getWeather, getAnalytics, getFields, createField, updateField, deleteField, getHistory, setRecommendationField, submitFeedback,
  retrainModel, getModelStatus, getGuidance, sendChat, getPlan,
  // aliases for existing call sites
  weather: getWeather, analytics: getAnalytics, fields: getFields, history: getHistory, feedback: submitFeedback,
}

import { create } from 'zustand'
import * as client from '@/api/client'
import type { Field, HistoryEntry, RecommendationResult, AnalyticsData, SoilInput } from '@/api/types'

export interface User {
  id: string
  name: string
  email: string
  picture: string
  provider: 'google'
}

interface State {
  fields: Field[]; history: HistoryEntry[]; analytics: AnalyticsData | null
  currentRecommendation: RecommendationResult | null
  loading: boolean; error: string | null
  user: User | null
  // compatibility aliases
  current: RecommendationResult | null
  fetchFields: () => Promise<void>
  fetchHistory: (params?: Record<string,string>) => Promise<void>
  fetchAnalytics: () => Promise<void>
  recommend: (d: SoilInput) => Promise<RecommendationResult>
  createField: (d: Partial<Field>) => Promise<void>
  updateField: (id: number, d: Partial<Field>) => Promise<void>
  deleteField: (id: number) => Promise<void>
  getFields: () => Promise<void>
  getHistory: (params?: Record<string,string>) => Promise<void>
  getAnalytics: () => Promise<void>
  setCurrent: (r: RecommendationResult | null) => void
  setCurrentRecommendation: (r: RecommendationResult | null) => void
  signInWithGoogle: () => Promise<void>
  signOut: () => void
}

const USER_KEY = 'cropwise.user'

function loadUser(): User | null {
  try { const raw = localStorage.getItem(USER_KEY); return raw ? JSON.parse(raw) as User : null } catch { return null }
}

export const useAppStore = create<State>((set, get) => ({
  fields: [], history: [], analytics: null,
  currentRecommendation: null, current: null,
  loading: false, error: null,
  user: loadUser(),

  fetchFields: async () => {
    set({ loading: true }); try { const fields = await client.getFields(); set({ fields, loading: false, error: null }) } catch (e: unknown) { set({ error: String(e), loading: false }) }
  },
  fetchHistory: async (p) => {
    set({ loading: true }); try { const history = await client.getHistory(p); set({ history, loading: false, error: null }) } catch (e: unknown) { set({ error: String(e), loading: false }) }
  },
  fetchAnalytics: async () => {
    set({ loading: true }); try { const analytics = await client.getAnalytics(); set({ analytics, loading: false, error: null }) } catch (e: unknown) { set({ error: String(e), loading: false }) }
  },
  recommend: async (d) => {
    set({ loading: true, error: null })
    try { const r = await client.recommend(d); set({ currentRecommendation: r, current: r, loading: false }); return r }
    catch (e: unknown) { set({ error: String(e), loading: false }); throw e }
  },
  createField: async (d) => { await client.createField(d); await get().fetchFields() },
  updateField: async (id, d) => { await client.updateField(id, d); await get().fetchFields() },
  deleteField: async (id) => { await client.deleteField(id); set({ fields: get().fields.filter(f=>f.id!==id)}) },
  getFields() { return get().fetchFields() },
  getHistory(p) { return get().fetchHistory(p) },
  getAnalytics() { return get().fetchAnalytics() },
  setCurrent: (r) => set({ current: r, currentRecommendation: r }),
  setCurrentRecommendation: (r) => set({ currentRecommendation: r, current: r }),

  // Mock OAuth — simulates a Google sign-in by waiting then creating a fake user.
  // Replace with a real /auth/google/callback flow when wiring up a backend.
  signInWithGoogle: async () => {
    await new Promise((r) => setTimeout(r, 800))
    const user: User = {
      id: 'g_' + Math.random().toString(36).slice(2, 10),
      name: 'Demo Farmer',
      email: 'farmer@example.com',
      picture: '',
      provider: 'google',
    }
    try { localStorage.setItem(USER_KEY, JSON.stringify(user)) } catch { /* ponytail: storage may be blocked in private mode */ }
    set({ user })
  },
  signOut: () => {
    try { localStorage.removeItem(USER_KEY) } catch { /* noop */ }
    set({ user: null })
  },
}))

export interface SoilInput {
  N: number; P: number; K: number
  temperature: number; humidity: number; ph: number; rainfall: number
  field_id?: number
  soil_type?: string | null
}
export interface CropRecommendation {
  crop: string; confidence: number
  model_confidence?: number
  adjustments?: string[]
  expected_yield?: number | null
}
export interface RecommendationResult {
  id: number; top_crops: CropRecommendation[]
  growing_guide: Record<string, { soil_prep: string; sowing: string; irrigation: string; harvest: string }>
  limiting_factor: string | null; created_at: string
  model_used?: boolean
  adjustment_notes?: string[]
  season?: string | null
  soil_type_applied?: string | null
  field_id?: number | null
  N?: number; P?: number; K?: number
  temperature?: number; humidity?: number; ph?: number; rainfall?: number
}
export interface Field {
  id: number; name: string
  latitude: number | null; longitude: number | null
  area_hectares: number | null; soil_type: string | null; created_at: string
  soil_n?: number | null; soil_p?: number | null; soil_k?: number | null; soil_ph?: number | null
  soil_tested_at?: string | null
}
export interface WeatherData { temperature: number; humidity: number; rainfall: number; source: string }
export interface AnalyticsData {
  feature_weights: Record<string, number>; feature_columns: string[]; weights: number[]
  accuracy: number; confusion_matrix: number[][]; classes: string[]; report: Record<string, unknown>
  cv_scores?: { '5fold_mean'?: number; '5fold_std'?: number }
  model_comparison?: Record<string, { cv3_mean: number; selected?: boolean; best_params?: Record<string, unknown> }>
  model_name?: string
  feature_importances?: Record<string, number>
  pso_cv_accuracy?: number | null
  trained_at?: string | null
  n_samples?: number | null
}
export interface ModelStatus {
  running: boolean
  last_started?: string | null
  last_error?: string | null
  last_result?: {
    feedback_rows?: number; total_rows?: number
    challenger_cv5?: number; incumbent_cv5?: number
    holdout_accuracy?: number; promoted?: boolean
    version?: number; note?: string
    yield_model?: { n_rows?: number; cv_r2_mean?: number } | null
    finished_at?: string
  } | null
}
export interface HistoryEntry {
  id: number; field_id: number | null
  N: number; P: number; K: number; temperature: number; humidity: number; ph: number; rainfall: number
  top_crops: CropRecommendation[]; created_at: string
  actual_crop?: string | null; actual_yield?: number | null
  feedback_rating?: number | null; feedback_notes?: string | null
}
export interface Feedback {
  recommendation_id: number; actual_crop?: string; actual_yield?: number; rating?: number; notes?: string
}
export interface StageDose { stage: string; share: string; products: string; adjusted_amount?: string | null }
export interface PestGuidance { pest: string; treatment: string; organic: string }
export interface NPKTriple { n: number; p: number; k: number }

export interface PlanOptions {
  field_id?: number
  N?: number; P?: number; K?: number
  temperature?: number; humidity?: number; ph?: number; rainfall?: number
  soil_type?: string
  include_ai?: boolean
}
export interface PlanProduct {
  name: string; kg_per_ha: number; kg_per_acre: number; bags_per_acre: number
}
export interface PlanStage {
  stage: string; share: string; products: string
  urea_kg?: number | null; dap_kg?: number | null; mop_kg?: number | null
}
export interface CropPlan {
  crop: string
  field?: { id?: number | null; name?: string | null } | null
  personalized: boolean
  basis: { weather?: string | null; soil?: string | null; personalized: boolean; notes: string[] }
  growing: {
    sowing: string; harvest: string; irrigation: string; soil_prep: string; risks: string[]
  }
  fertilizer: {
    unit: string
    target?: NPKTriple | null
    available?: NPKTriple | null
    deficit?: NPKTriple | null
    products: PlanProduct[]
    stages: PlanStage[]
    personalized: boolean
    ph_advice?: string | null
    notes: string[]
  }
  pests: PestGuidance[]
  ai_explanation?: string | null
}
export interface GuidanceResult {
  crop: string
  soil_type_applied?: string | null
  fertilizer: {
    unit: string
    total_npk?: NPKTriple | null
    deficit?: NPKTriple | null
    personalized: boolean
    stages: StageDose[]
    soil_practices: string[]
    ph_advice?: string | null
    notes: string[]
  }
  pests: PestGuidance[]
  source_note: string
}

export interface ChatMessage { role: 'user' | 'assistant'; content: string }
export interface ChatReply { reply: string }

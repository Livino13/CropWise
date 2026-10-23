import type { RecommendationResult, CropPlan, PlanOptions } from "@/api/types";
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect, useCallback, useMemo } from 'react'
import { Dialog } from '@headlessui/react'
import { useAppStore } from '@/stores/appStore'
import { Card, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Accordion } from '@/components/ui/Accordion'
import { CropPlanView } from '@/components/CropPlanView'
import { cropEmoji, cropLabel, cropPhoto, CROP_META } from '@/utils/cropMeta'
import { confidenceColor, confidenceLabel } from '@/utils/helpers'
import { api } from '@/api/client'

function whyText(crop: string, conf: number){
  const m = CROP_META[crop]
  if(!m) return `Model confidence ${(conf*100).toFixed(0)}%.`
  return `${m.description} Best in ${m.season} season · Water need: ${m.waterNeed}. Matched on NPK, pH and climate.`
}

function PlanDialog({ crop, options, onClose, cache, setCache }: {
  crop: string | null
  options: PlanOptions
  onClose: () => void
  cache: Record<string, CropPlan>
  setCache: (crop: string, plan: CropPlan) => void
}) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [explaining, setExplaining] = useState(false)
  const plan = crop ? cache[crop] : null

  useEffect(() => {
    setError('')
    setExplaining(false)
    if (!crop || plan) {
      setLoading(false)
      return
    }
    let alive = true
    setLoading(true)
    api.getPlan(crop, options)
      .then((result) => { if (alive) { setCache(crop, result); setLoading(false) } })
      .catch(() => { if (alive) { setError('Field plan unavailable right now — try again.'); setLoading(false) } })
    return () => { alive = false }
  }, [crop, plan, options, setCache])

  async function explain() {
    if (!crop) return
    setExplaining(true)
    setError('')
    try {
      const result = await api.getPlan(crop, { ...options, include_ai: true })
      if (!result.ai_explanation) throw new Error('no explanation')
      setCache(crop, result)
    } catch {
      setError('Could not write the explanation right now. Please try again.')
    } finally {
      setExplaining(false)
    }
  }

  return (
    <Dialog open={crop !== null} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-2xl bg-white shadow-xl">
          {crop && (
            <>
              <div className="sticky top-0 z-10 flex items-center justify-between border-b border-stone-200 bg-white px-4 py-3">
                <Dialog.Title className="text-lg font-bold">{cropLabel(crop)} field plan</Dialog.Title>
                <button
                  type="button"
                  onClick={onClose}
                  aria-label="Close field plan"
                  className="w-8 h-8 rounded-full bg-stone-100 text-stone-600 grid place-items-center hover:bg-stone-200"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4" aria-hidden>
                    <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
                  </svg>
                </button>
              </div>
              <div className="p-4">
                {(loading || (crop !== null && !plan && !error)) && (
                  <p className="text-xs text-stone-400">Calculating your field plan…</p>
                )}
                {error && <p className="mb-2 text-xs text-amber-600">{error}</p>}
                {plan && <CropPlanView plan={plan} onExplain={explain} explaining={explaining} />}
              </div>
            </>
          )}
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}

export default function Result() {
  const loc = useLocation()
  const nav = useNavigate()
  const stored = useAppStore(s=>s.current)
  // History page passes { fromHistory: entry }; recommend flow passes the result directly.
  const raw = loc.state as Record<string, unknown> | null
  const fromHistory = raw && typeof raw === 'object' && 'fromHistory' in raw
    ? (raw.fromHistory as RecommendationResult)
    : null
  const data = fromHistory || (raw as unknown as RecommendationResult) || stored
  const { fields, fetchFields } = useAppStore()
  const [saveFieldId, setSaveFieldId] = useState<string>('')
  const [saving, setSaving] = useState(false)
  const [savedMsg, setSavedMsg] = useState('')
  const [showConfetti, setShowConfetti] = useState(false)
  const [planCache, setPlanCache] = useState<Record<string, CropPlan>>({})
  const [planCrop, setPlanCrop] = useState<string | null>(null)
  const cachePlan = useCallback((crop: string, plan: CropPlan) => {
    setPlanCache(prev => ({ ...prev, [crop]: plan }))
  }, [])
  const planOptions = useMemo<PlanOptions>(() => ({
    field_id: data?.field_id ?? undefined,
    N: data?.N,
    P: data?.P,
    K: data?.K,
    temperature: data?.temperature,
    humidity: data?.humidity,
    ph: data?.ph,
    rainfall: data?.rainfall,
    soil_type: data?.soil_type_applied ?? undefined,
  }), [data])
  useEffect(()=>{ fetchFields() }, [fetchFields])
  const topConf = data?.top_crops?.[0]?.confidence ?? 0
  useEffect(()=>{ if(topConf >= 0.9) { setShowConfetti(true); const t=setTimeout(()=>setShowConfetti(false), 3000); return ()=>clearTimeout(t) } }, [topConf])
  const saveToField = async () => {
    if(!saveFieldId || !data?.id) return
    setSaving(true); setSavedMsg('')
    try {
      await api.setRecommendationField(Number(data.id), Number(saveFieldId))
      setSavedMsg('Saved!')
    } catch { setSavedMsg('Save failed') } finally { setSaving(false) }
  }

  if(!data || !data.top_crops){
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <div className="text-4xl mb-4">🌱</div>
        <p className="text-stone-500 mb-4">No recommendation yet.</p>
        <Link to="/recommend"><Button>New Recommendation</Button></Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Your Recommendations</h1>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={()=>nav('/recommend')}>New</Button>
          <Link to="/history"><Button variant="ghost">History</Button></Link>
        </div>
      </div>

      {data.limiting_factor && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-sm text-amber-800 flex gap-3">
          <span>⚠️</span><span>{data.limiting_factor}</span>
        </div>
      )}

      {data.model_used === false && (
        <div className="p-4 rounded-xl bg-stone-100 border border-stone-200 text-sm text-stone-600 flex gap-3">
          <span>ℹ️</span><span>Trained model unavailable — these results come from a basic rule-based fallback. Run <code className="font-mono">train.py</code> and restart the backend for ML predictions.</span>
        </div>
      )}

      {(data.adjustment_notes?.length ?? 0) > 0 && (
        <div className="p-4 rounded-xl bg-brand-50 border border-brand-200 text-sm text-brand-900">
          <div className="font-semibold mb-1">Adjusted for your context ({data.season} season{data.soil_type_applied ? `, ${data.soil_type_applied} soil` : ''})</div>
          <ul className="list-disc list-inside space-y-0.5 text-xs text-brand-800">
            {data.adjustment_notes!.map((n, i) => <li key={i}>{n}</li>)}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {data.top_crops.map((c, i:number)=>(
          <Card key={c.crop} className={`${i===0?'ring-2 ring-brand-500 shadow-md':''} overflow-hidden`}>
            <div className={`h-1 ${i===0?'bg-brand-500':i===1?'bg-amber-400':'bg-stone-300'}`} />
            <CardBody>
              <div className="relative w-full h-32 -mt-2 -mx-2 mb-3 overflow-hidden rounded-lg bg-stone-100">
                {cropPhoto(c.crop) ? (
                  <img src={cropPhoto(c.crop)!} alt={c.crop} className="w-full h-full object-cover" loading="lazy" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-5xl">{cropEmoji(c.crop)}</div>
                )}
                <div className="absolute top-2 right-2">
                  {i===0 && <span className="text-xs font-bold bg-brand-600 text-white px-2 py-1 rounded-full">#1</span>}
                  {i===1 && <span className="text-xs font-bold bg-stone-200 text-stone-600 px-2 py-1 rounded-full">#2</span>}
                  {i===2 && <span className="text-xs font-bold bg-stone-100 text-stone-500 px-2 py-1 rounded-full">#3</span>}
                </div>
              </div>
              <div className="font-bold text-lg leading-tight">{cropLabel(c.crop)}</div>
              <div className={`mt-2 inline-flex items-center gap-1.5 text-sm font-semibold px-2.5 py-1 rounded-full border ${confidenceColor(c.confidence)}`}>
                {(c.confidence*100).toFixed(1)}% · {confidenceLabel(c.confidence)}
              </div>
              {c.model_confidence != null && Math.abs(c.model_confidence - c.confidence) > 0.005 && (
                <div className="text-[11px] text-stone-400 mt-1">model {Math.round(c.model_confidence*100)}% → adjusted</div>
              )}
              {(c.adjustments?.length ?? 0) > 0 && (
                <ul className="mt-2 space-y-0.5">
                  {c.adjustments!.map((a, j) => (
                    <li key={j} className="text-[11px] text-stone-500 flex gap-1"><span>{a.includes('(+)') ? '✅' : '⚠️'}</span><span>{a}</span></li>
                  ))}
                </ul>
              )}
              {c.expected_yield != null && (
                <div className="text-xs text-brand-700 mt-2 font-medium">≈ {c.expected_yield.toFixed(2)} t/ha expected yield</div>
              )}
              <div className="mt-3">
                <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
                  <div className="h-full bg-brand-500 rounded-full transition-all" style={{width:`${Math.round(c.confidence*100)}%`}} />
                </div>
              </div>
              <p className="text-xs text-stone-500 mt-3 leading-relaxed">{whyText(c.crop, c.confidence)}</p>
              <div className="mt-4 space-y-2">
                <Accordion title="Growing guide">
                  <div className="space-y-2 text-xs leading-relaxed">
                    {(() => {
                      const g = data.growing_guide?.[c.crop]
                      if(!g) return <p>Open the field plan below for growing guidance for {cropLabel(c.crop)}.</p>
                      return (<>
                        <div><span className="font-semibold">Soil:</span> {g.soil_prep}</div>
                        <div><span className="font-semibold">Sowing:</span> {g.sowing}</div>
                        <div><span className="font-semibold">Water:</span> {g.irrigation}</div>
                        <div><span className="font-semibold">Harvest:</span> {g.harvest}</div>
                      </>)
                    })()}
                  </div>
                </Accordion>
                <button
                  type="button"
                  onClick={() => setPlanCrop(c.crop)}
                  className="w-full flex items-center justify-between border border-stone-200 rounded-lg px-4 py-3 text-sm font-medium bg-stone-50 hover:bg-stone-100"
                >
                  <span>🌾 Field plan</span>
                  <span className="text-stone-400" aria-hidden>→</span>
                </button>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      <PlanDialog
        crop={planCrop}
        options={planOptions}
        onClose={() => setPlanCrop(null)}
        cache={planCache}
        setCache={cachePlan}
      />

      {showConfetti && <div className="text-center text-2xl animate-[fadeUp_0.6s_ease-out]" aria-hidden>🎉 Excellent match! 🎉</div>}
      <Card>
        <CardBody>
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex items-end gap-2">
              <label className="text-sm font-medium text-stone-700">Save to field</label>
              <select value={saveFieldId} onChange={e=>setSaveFieldId(e.target.value)} className="rounded-lg border border-stone-300 px-3 py-2 text-sm">
                <option value="">— Select field —</option>
                {fields.map(f=><option key={f.id} value={f.id}>{f.name}</option>)}
              </select>
              <Button size="sm" onClick={saveToField} disabled={!saveFieldId || saving}>{saving?'Saving…':'Save'}</Button>
              {savedMsg && <span className="text-xs text-stone-500">{savedMsg}</span>}
            </div>
            <span className="text-stone-300">·</span>
            <Link to="/recommend"><Button variant="secondary">← New recommendation</Button></Link>
            <Link to="/guide"><Button variant="ghost">How recommendations work</Button></Link>
          </div>
          <p className="text-xs text-stone-400 mt-3">These are starting suggestions, not guarantees. Confirm with your local agronomist before planting.</p>
        </CardBody>
      </Card>
    </div>
  )
}

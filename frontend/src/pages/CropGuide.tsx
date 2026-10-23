import { useEffect, useMemo, useRef, useState } from 'react'
import { Dialog } from '@headlessui/react'
import { Card, CardBody } from '@/components/ui/Card'
import { CropPlanView } from '@/components/CropPlanView'
import { api } from '@/api/client'
import type { CropPlan } from '@/api/types'
import { useAppStore } from '@/stores/appStore'
import { CROP_META, cropEmoji, cropLabel, cropPhoto } from '@/utils/cropMeta'

const CROPS = Object.entries(CROP_META)
  .map(([key, m]) => ({ key, ...m }))
  .sort((a, b) => a.key.localeCompare(b.key))

const CONFIDENCE_BANDS = [
  { label: 'Excellent match', range: '70% or more', cls: 'text-green-700 bg-green-50 border-green-200', hint: 'Strong fit for your soil and weather.' },
  { label: 'Good match', range: '40–69%', cls: 'text-amber-700 bg-amber-50 border-amber-200', hint: 'Likely suitable — check water and market needs.' },
  { label: 'Moderate', range: 'below 40%', cls: 'text-stone-600 bg-stone-50 border-stone-200', hint: 'Treat as a starting point; a soil test or local advice helps.' },
]

const SOIL_TERMS = [
  ['N — Nitrogen', 'Helps leaves and stems grow. Low nitrogen often shows as pale, yellowish leaves.'],
  ['P — Phosphorus', 'Helps roots, flowering and early growth.'],
  ['K — Potassium', 'Helps plant health, disease resistance and grain or fruit quality.'],
  ['pH', 'How acidic or alkaline the soil is. Most crops do best between about 6 and 7.5.'],
  ['Rainfall', 'The water your crop receives across the season.'],
  ['Humidity', 'Moisture in the air. High humidity can increase disease pressure.'],
]

function seasonForMonth(month: number) {
  if (month >= 5 && month <= 8) return { name: 'Kharif', months: 'Jun–Sep' }
  if (month >= 9 || month <= 1) return { name: 'Rabi', months: 'Oct–Feb' }
  return { name: 'Zaid', months: 'Mar–May' }
}

export default function CropGuide() {
  const season = useMemo(() => seasonForMonth(new Date().getMonth()), [])
  const inSeason = CROPS.filter(
    (c) =>
      c.season.toLowerCase().includes(season.name.toLowerCase()) ||
      c.season.toLowerCase().includes('year-round'),
  )

  const [selected, setSelected] = useState<string | null>(null)
  const [plan, setPlan] = useState<CropPlan | null>(null)
  const [guideLoading, setGuideLoading] = useState(false)
  const [guideError, setGuideError] = useState('')
  const [explaining, setExplaining] = useState(false)
  const [fieldId, setFieldId] = useState<number | ''>('')
  const requestRef = useRef(0)
  const fields = useAppStore((s) => s.fields)
  const fetchFields = useAppStore((s) => s.fetchFields)

  useEffect(() => { fetchFields() }, [fetchFields])

  const meta = selected ? CROP_META[selected] : null

  function loadPlan(crop: string) {
    const id = ++requestRef.current
    setSelected(crop)
    setPlan(null)
    setGuideError('')
    setGuideLoading(true)
    setExplaining(false)
    api.getPlan(crop, {
      field_id: fieldId === '' ? undefined : fieldId,
    })
      .then((p) => { if (requestRef.current === id) setPlan(p) })
      .catch(() => { if (requestRef.current === id) setGuideError('A field plan is unavailable right now. Please try again.') })
      .finally(() => { if (requestRef.current === id) setGuideLoading(false) })
  }

  function openCrop(crop: string) {
    loadPlan(crop)
  }

  async function explainPlan() {
    if (!selected) return
    const requestId = requestRef.current
    setExplaining(true)
    setGuideError('')
    try {
      const explained = await api.getPlan(selected, {
        field_id: fieldId === '' ? undefined : fieldId,
        include_ai: true,
      })
      if (requestRef.current !== requestId) return
      if (!explained.ai_explanation) throw new Error('no explanation')
      setPlan(explained)
    } catch {
      if (requestRef.current === requestId) {
        setGuideError('Could not write the explanation right now. Please try again.')
      }
    } finally {
      if (requestRef.current === requestId) setExplaining(false)
    }
  }

  function closeCrop() {
    requestRef.current++
    setSelected(null)
    setPlan(null)
    setGuideError('')
    setGuideLoading(false)
    setExplaining(false)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Crop Guide</h1>
        <p className="text-sm text-stone-500 mt-1">Know what to grow — and how to read your recommendation.</p>
      </div>

      <Card>
        <CardBody>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 className="font-semibold text-stone-800 text-sm">Personalize with your field</h2>
              <p className="text-xs text-stone-500 mt-0.5">
                Plans use the field's soil test and a 7-day weather forecast. Without a field you still get a standard crop plan.
              </p>
            </div>
            <select
              value={fieldId}
              onChange={(e) => {
                const value = e.target.value
                setFieldId(value === '' ? '' : Number(value))
                if (selected) closeCrop()
              }}
              className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm min-w-[220px]"
              aria-label="Choose a field to personalize crop plans"
            >
              <option value="">No field — standard plan</option>
              {fields.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name}{f.soil_type ? ` · ${f.soil_type}` : ''}
                </option>
              ))}
            </select>
          </div>
          {fields.length === 0 && (
            <p className="text-[11px] text-stone-400 mt-2">
              No saved fields yet. Add one on the Fields page to unlock soil-based plans.
            </p>
          )}
        </CardBody>
      </Card>

      {inSeason.length > 0 && (
        <Card>
          <CardBody>
            <div className="flex items-center justify-between gap-2">
              <h2 className="font-semibold text-stone-800">In season now</h2>
              <span className="text-xs font-medium text-brand-700 bg-brand-50 border border-brand-200 rounded-full px-2.5 py-0.5">
                {season.name} · {season.months}
              </span>
            </div>
            <p className="text-xs text-stone-500 mt-0.5">Crops commonly sown in this season. Local weather and irrigation still matter.</p>
            <div className="mt-3 flex gap-3 overflow-x-auto pb-1">
              {inSeason.map((c) => {
                const photo = cropPhoto(c.key)
                return (
                  <button
                    type="button"
                    key={c.key}
                    onClick={() => openCrop(c.key)}
                    className="w-32 shrink-0 text-left rounded-xl border border-stone-200 overflow-hidden bg-white hover:shadow-sm transition-shadow"
                  >
                    <div className="h-20 bg-stone-100">
                      {photo ? (
                        <img src={photo} alt={c.key} className="w-full h-full object-cover" loading="lazy" />
                      ) : (
                        <div className="w-full h-full grid place-items-center text-2xl">{cropEmoji(c.key)}</div>
                      )}
                    </div>
                    <div className="p-2">
                      <div className="text-xs font-semibold text-stone-800 truncate">{cropLabel(c.key)}</div>
                      <div className="text-[10px] text-stone-500">{c.waterNeed} water</div>
                    </div>
                  </button>
                )
              })}
            </div>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardBody>
          <h2 className="font-semibold text-stone-800">Understand your result</h2>
          <p className="text-xs text-stone-500 mt-0.5">
            CropWise compares your soil and weather with thousands of farm records and shows the three closest matches.
          </p>
          <div className="mt-3 space-y-2">
            {CONFIDENCE_BANDS.map((b) => (
              <div key={b.label} className="flex flex-wrap items-center gap-x-3 gap-y-1">
                <span className={`w-28 text-center rounded-full border px-2 py-0.5 text-xs font-medium ${b.cls}`}>{b.label}</span>
                <span className="w-20 text-xs text-stone-500 tabular-nums">{b.range}</span>
                <span className="text-xs text-stone-500">{b.hint}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-stone-500 mt-3 pt-3 border-t border-stone-100">
            The top 3 are best matches, not guarantees. If confidence is low, check your soil values or ask a local agronomist.
          </p>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <h2 className="font-semibold text-stone-800">Know your soil numbers</h2>
          <p className="text-xs text-stone-500 mt-0.5">The values CropWise asks for — and what they mean for your crop.</p>
          <div className="mt-3 grid sm:grid-cols-2 gap-2.5">
            {SOIL_TERMS.map(([term, desc]) => (
              <div key={term} className="rounded-lg border border-stone-100 bg-stone-50 p-3">
                <div className="text-sm font-semibold text-stone-800">{term}</div>
                <div className="text-xs text-stone-500 mt-0.5">{desc}</div>
              </div>
            ))}
          </div>
          <p className="text-xs text-stone-500 mt-3">A soil test every 2–3 years is the most reliable way to get these values.</p>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <h2 className="font-semibold text-stone-800">All supported crops</h2>
          <p className="text-xs text-stone-500 mt-0.5">{CROPS.length} crops the model can recommend.</p>
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {CROPS.map((c) => {
              const photo = cropPhoto(c.key)
              return (
                <button
                  type="button"
                  key={c.key}
                  onClick={() => openCrop(c.key)}
                  className="text-left rounded-xl border border-stone-200 overflow-hidden bg-white hover:shadow-sm transition-shadow"
                >
                  <div className="relative h-20 bg-stone-100">
                    {photo ? (
                      <img src={photo} alt={c.key} className="w-full h-full object-cover" loading="lazy" />
                    ) : (
                      <div className="w-full h-full grid place-items-center text-3xl">{cropEmoji(c.key)}</div>
                    )}
                  </div>
                  <div className="p-2.5">
                    <div className="text-sm font-semibold text-stone-800 leading-tight">{cropLabel(c.key)}</div>
                    <div className="text-[11px] text-stone-500 mt-0.5">{c.season} · {c.waterNeed} water</div>
                  </div>
                </button>
              )
            })}
          </div>
        </CardBody>
      </Card>

      <Dialog open={selected !== null} onClose={closeCrop} className="relative z-50">
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-2xl bg-white shadow-xl">
            {meta && selected && (
              <>
                <div className="relative h-40 bg-stone-100">
                  {cropPhoto(selected) ? (
                    <img src={cropPhoto(selected)!} alt={selected} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full grid place-items-center text-5xl">{cropEmoji(selected)}</div>
                  )}
                  <button
                    onClick={closeCrop}
                    aria-label="Close crop details"
                    className="absolute top-2 right-2 w-8 h-8 rounded-full bg-black/50 text-white grid place-items-center hover:bg-black/60"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4" aria-hidden>
                      <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
                    </svg>
                  </button>
                </div>
                <div className="p-4 space-y-3">
                  <div>
                    <Dialog.Title className="text-lg font-bold">{cropLabel(selected)}</Dialog.Title>
                    <div className="text-xs text-stone-500 mt-0.5">{meta.season} · {meta.waterNeed} water</div>
                  </div>
                  <p className="text-sm text-stone-600">{meta.description}</p>

                  {guideLoading && <p className="text-xs text-stone-400">Calculating your field plan…</p>}
                  {guideError && <p className="text-xs text-amber-600">{guideError}</p>}
                  {fieldId === '' && plan && (
                    <p className="text-[11px] text-stone-400">
                      Tip: choose a saved field above for soil-test and weather-based numbers.
                    </p>
                  )}

                  {plan && (
                    <CropPlanView
                      plan={plan}
                      onExplain={explainPlan}
                      explaining={explaining}
                    />
                  )}
                </div>
              </>
            )}
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppStore } from '@/stores/appStore'
import { api } from '@/api/client'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

export default function NewRecommendation() {
  const nav = useNavigate()
  const location = useLocation()
  const { fields, fetchFields, recommend, loading, error } = useAppStore()
  useEffect(()=>{ fetchFields() }, [])

  const [form, setForm] = useState({ N:50, P:40, K:40, temperature:25, humidity:65, ph:6.5, rainfall:100, field_id:'' })
  const [loc, setLoc] = useState({ lat:'', lon:'' })
  const [weatherMsg, setWeatherMsg] = useState('')
  const [weatherLoading, setWeatherLoading] = useState(false)

  // Pre-fill from History "Re-run": { fromHistory: entry }
  useEffect(() => {
    const h = (location.state as { fromHistory?: Record<string, number | string | null> } | null)?.fromHistory
    if (h && typeof h.N === 'number') {
      setForm({
        N: Number(h.N), P: Number(h.P), K: Number(h.K),
        temperature: Number(h.temperature), humidity: Number(h.humidity),
        ph: Number(h.ph), rainfall: Number(h.rainfall),
        field_id: h.field_id != null ? String(h.field_id) : '',
      })
      setWeatherMsg('Pre-filled from a past recommendation — adjust and re-run.')
    }
  }, [location.state])

  const set = (k:string,v:number|string)=> setForm(s=>({...s,[k]:v}))

  // Auto-fill from the selected field: soil test NPK/pH + climate normals from its lat/lon
  const selectedField = fields.find(f => String(f.id) === String(form.field_id))
  useEffect(() => {
    if (!selectedField) return
    const notes: string[] = []
    if (selectedField.soil_n != null || selectedField.soil_p != null || selectedField.soil_k != null || selectedField.soil_ph != null) {
      setForm(s => ({
        ...s,
        N: selectedField.soil_n ?? s.N,
        P: selectedField.soil_p ?? s.P,
        K: selectedField.soil_k ?? s.K,
        ph: selectedField.soil_ph ?? s.ph,
      }))
      notes.push(`NPK/pH from field's soil test`)
    }
    if (selectedField.latitude != null && selectedField.longitude != null) {
      setLoc({ lat: String(selectedField.latitude), lon: String(selectedField.longitude) })
      api.weather(selectedField.latitude, selectedField.longitude)
        .then(w => {
          setForm(s => ({
            ...s,
            temperature: Math.min(60, Math.max(-10, w.temperature)),
            humidity: Math.min(100, Math.max(0, w.humidity)),
            rainfall: Math.min(1000, Math.max(0, w.rainfall)),
          }))
          setWeatherMsg(`Climate normals from field location (${w.source})`)
        })
        .catch(() => {})
    }
    if (notes.length) setWeatherMsg(notes.join(' · '))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedField?.id])

  const detectLocation = () => {
    navigator.geolocation.getCurrentPosition(
      p=> setLoc({ lat: p.coords.latitude.toFixed(4), lon: p.coords.longitude.toFixed(4) }),
      ()=> setWeatherMsg('Location denied')
    )
  }

  const autoFillWeather = async () => {
    const lat = parseFloat(loc.lat), lon = parseFloat(loc.lon)
    if(isNaN(lat)||isNaN(lon)) { setWeatherMsg('Enter lat/lon first'); return }
    try {
      setWeatherLoading(true); setWeatherMsg('Fetching weather…')
      const w = await api.weather(lat, lon)
      // clamp to backend SoilInput limits so auto-fill never produces a 422
      setForm(s=>({...s,
        temperature: Math.min(60, Math.max(-10, w.temperature)),
        humidity: Math.min(100, Math.max(0, w.humidity)),
        rainfall: Math.min(1000, Math.max(0, w.rainfall)),
      }))
      setWeatherMsg(`Filled from ${w.source}: ${w.temperature}°C, ${w.humidity}% humidity, ${w.rainfall}mm rain`)
    } catch { setWeatherMsg('Weather fetch failed — using estimates') } finally { setWeatherLoading(false) }
  }

  const [errors, setErrors] = useState<Record<string,string>>({})
  const validate = (): boolean => {
    const e: Record<string,string> = {}
    const num = (v:unknown)=> Number(v)
    if(isNaN(num(form.N))||num(form.N)<0||num(form.N)>200) e.N='0–200'
    if(isNaN(num(form.P))||num(form.P)<0||num(form.P)>200) e.P='0–200'
    if(isNaN(num(form.K))||num(form.K)<0||num(form.K)>250) e.K='0–250'
    if(isNaN(num(form.ph))||num(form.ph)<0||num(form.ph)>14) e.ph='0–14'
    if(isNaN(num(form.humidity))||num(form.humidity)<0||num(form.humidity)>100) e.humidity='0–100'
    if(isNaN(num(form.rainfall))||num(form.rainfall)<0||num(form.rainfall)>1000) e.rainfall='0–1000'
    if(isNaN(num(form.temperature))||num(form.temperature)<-10||num(form.temperature)>60) e.temperature='-10–60'
    setErrors(e); return Object.keys(e).length===0
  }
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if(!validate()) return
    const payload: Record<string, number | string | null> = {
      N: Number(form.N), P: Number(form.P), K: Number(form.K),
      temperature: Number(form.temperature), humidity: Number(form.humidity),
      ph: Number(form.ph), rainfall: Number(form.rainfall),
    }
    if(form.field_id) payload.field_id = Number(form.field_id)
    if(selectedField?.soil_type) payload.soil_type = selectedField.soil_type
    try {
      const res = await recommend(payload as never)
      nav('/result', { state: res })
    } catch {}
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">New Recommendation</h1>

      <form onSubmit={submit} className="space-y-6">
        <Card>
          <CardHeader><h2 className="font-semibold">Soil Nutrients</h2><p className="text-xs text-stone-500 mt-1">Enter lab results or estimated values</p></CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Input label="Nitrogen (N) — kg/ha" type="number" value={form.N} onChange={e=>set('N',e.target.value)} min={0} max={200} step={1} error={errors.N} />
              <Input label="Phosphorus (P) — kg/ha" type="number" value={form.P} onChange={e=>set('P',e.target.value)} min={0} max={200} step={1} error={errors.P} />
              <Input label="Potassium (K) — kg/ha" type="number" value={form.K} onChange={e=>set('K',e.target.value)} min={0} max={250} step={1} error={errors.K} />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><h2 className="font-semibold">Climate & Soil</h2></CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-stone-700 mb-1 block">pH — {form.ph}</label>
                <input type="range" min={0} max={14} step={0.1} value={form.ph} onChange={e=>set('ph',parseFloat(e.target.value))} className="w-full accent-brand-600" />
                <div className="flex justify-between text-xs text-stone-400"><span>Acidic</span><span>Neutral 7</span><span>Alkaline</span></div>
                  {errors.ph && <span className="text-xs text-red-500">{errors.ph}</span>}
              </div>
              <Input label="Temperature — °C" type="number" value={form.temperature} onChange={e=>set('temperature',e.target.value)} step={0.5} error={errors.temperature} />
              <Input label="Humidity — %" type="number" value={form.humidity} onChange={e=>set('humidity',e.target.value)} min={0} max={100} error={errors.humidity} />
              <Input label="Rainfall — mm" type="number" value={form.rainfall} onChange={e=>set('rainfall',e.target.value)} min={0} error={errors.rainfall} />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><h2 className="font-semibold">Location & Weather</h2><p className="text-xs text-stone-500">Auto-fill climate from coordinates via Open-Meteo</p></CardHeader>
          <CardBody>
            <div className="flex flex-wrap gap-3 items-end">
              <div className="flex-1 min-w-[120px]"><Input label="Latitude" value={loc.lat} onChange={e=>setLoc(s=>({...s,lat:e.target.value}))} placeholder="28.61" /></div>
              <div className="flex-1 min-w-[120px]"><Input label="Longitude" value={loc.lon} onChange={e=>setLoc(s=>({...s,lon:e.target.value}))} placeholder="77.23" /></div>
              <Button type="button" variant="secondary" onClick={detectLocation}>📍 My location</Button>
              <Button type="button" variant="secondary" onClick={autoFillWeather} disabled={weatherLoading}>{weatherLoading?'…':'☁️ Auto-fill weather'}</Button>
            </div>
            {weatherMsg && <p className="text-xs text-stone-500 mt-2">{weatherMsg}</p>}
            {fields.length>0 && (
              <div className="mt-4">
                <label className="text-sm font-medium text-stone-700 block mb-1">Link to field (optional)</label>
                <select value={form.field_id} onChange={e=>set('field_id',e.target.value)} className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm">
                  <option value="">— No field —</option>
                  {fields.map(f=><option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
              </div>
            )}
          </CardBody>
        </Card>

        {error && <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">{error}</div>}

        <Button type="submit" size="lg" disabled={loading} className="w-full">
          {loading ? 'Analyzing…' : '✦ Get Recommendation'}
        </Button>
      </form>
    </div>
  )
}

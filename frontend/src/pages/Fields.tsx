import { useEffect, useState } from 'react'
import 'leaflet/dist/leaflet.css'
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet'
import '@/hooks/useLeafletFix'
import { useAppStore } from '@/stores/appStore'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Dialog } from '@headlessui/react'
import type { Field } from '@/api/types'
import { cropLabel } from '@/utils/cropMeta'


function FieldPicker({ lat, lon, onPick }: { lat:number|null, lon:number|null, onPick:(lat:number,lon:number)=>void }){
  useMapEvents({ click(e){ onPick(e.latlng.lat, e.latlng.lng) } })
  return lat!=null && lon!=null ? <Marker position={[lat, lon]} /> : null
}

const SOIL_TYPES = ['Alluvial', 'Black', 'Red', 'Sandy', 'Loamy', 'Clayey', 'Laterite']

export default function Fields() {
  const { fields, history, fetchFields, fetchHistory, createField, updateField, deleteField } = useAppStore()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Field | null>(null)
  const [form, setForm] = useState<Partial<Field>>({ name:'', latitude:null, longitude:null, area_hectares:null, soil_type:null })
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')
  const [soilField, setSoilField] = useState<Field | null>(null)
  const [soilForm, setSoilForm] = useState({ soil_n: null as number|null, soil_p: null as number|null, soil_k: null as number|null, soil_ph: null as number|null })
  const [soilSaving, setSoilSaving] = useState(false)
  const [soilError, setSoilError] = useState('')

  useEffect(()=>{ fetchFields(); fetchHistory() }, [fetchFields, fetchHistory])

  const start = (f?: Field) => {
    if(f){ setEditing(f); setForm({ ...f }) }
    else { setEditing(null); setForm({ name:'', latitude:null, longitude:null, area_hectares:null, soil_type:null }) }
    setFormError('')
    setOpen(true)
  }
  const startSoilTest = (f: Field) => {
    setSoilField(f)
    setSoilForm({ soil_n: f.soil_n ?? null, soil_p: f.soil_p ?? null, soil_k: f.soil_k ?? null, soil_ph: f.soil_ph ?? null })
    setSoilError('')
  }
  const saveSoilTest = async () => {
    if(!soilField) return
    setSoilError('')
    setSoilSaving(true)
    try {
      await updateField(soilField.id, { ...soilForm })
      setSoilField(null)
    } catch (e: unknown) {
      setSoilError(e instanceof Error ? e.message : String(e))
    } finally { setSoilSaving(false) }
  }
  const num = (v: string) => v === '' ? null : (isNaN(parseFloat(v)) ? null : parseFloat(v))
  const save = async () => {
    if(!form.name?.trim()) { setFormError('Name is required'); return }
    // empty string is rejected by the backend validator — send null instead
    const payload: Partial<Field> = { ...form, name: form.name.trim(), soil_type: form.soil_type?.trim() ? form.soil_type : null }
    setFormError('')
    setSaving(true)
    try {
      if(editing) await updateField(editing.id, payload)
      else await createField(payload)
      setOpen(false)
    } catch (e: unknown) {
      setFormError(e instanceof Error ? e.message : String(e))
    } finally { setSaving(false) }
  }

  const recsFor = (id:number) => history.filter(h => h.field_id === id)

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Fields</h1>
        <Button onClick={()=>start()}>+ Add Field</Button>
      </div>

      {fields.length===0 ? (
        <Card><CardBody>
          <div className="text-center py-12 text-stone-400">
            <div className="text-4xl mb-3">◈</div>
            <p>No fields yet</p>
            <Button className="mt-4" onClick={()=>start()}>Add your first field</Button>
          </div>
        </CardBody></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {fields.map(f=>{
            const recs = recsFor(f.id)
            return (
              <Card key={f.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">{f.name}</h3>
                    <div className="flex gap-1">
                      <Button size="sm" variant="ghost" onClick={()=>startSoilTest(f)}>🧪 Test</Button>
                      <Button size="sm" variant="ghost" onClick={()=>start(f)}>Edit</Button>
                      <Button size="sm" variant="ghost" onClick={async()=>{ if(confirm('Delete this field?')) await deleteField(f.id) }}>✕</Button>
                    </div>
                  </div>
                </CardHeader>
                <CardBody>
                  <div className="text-sm text-stone-500 space-y-1">
                    {f.soil_type && <div>🌱 {f.soil_type}</div>}
                    {f.area_hectares!=null && <div>📐 {f.area_hectares} ha</div>}
                    {f.latitude!=null && <div>📍 <a className="text-brand-600 hover:underline" href={`https://www.openstreetmap.org/?mlat=${f.latitude}&mlon=${f.longitude}`} target="_blank" rel="noreferrer">{f.latitude.toFixed(3)}, {f.longitude?.toFixed(3)}</a></div>}
                  </div>
                  <div className="mt-3 pt-3 border-t border-stone-100">
                    <div className="text-xs text-stone-400 mb-1">Soil test</div>
                    {f.soil_n==null && f.soil_p==null && f.soil_k==null && f.soil_ph==null ? (
                      <p className="text-xs text-stone-400">No lab test recorded</p>
                    ) : (
                      <div className="text-xs text-stone-600">
                        <div>N {f.soil_n ?? '—'} · P {f.soil_p ?? '—'} · K {f.soil_k ?? '—'} · pH {f.soil_ph ?? '—'}</div>
                        {f.soil_tested_at && <div className="text-stone-400 mt-0.5">tested {new Date(f.soil_tested_at).toLocaleDateString()}</div>}
                      </div>
                    )}
                  </div>
                  <div className="mt-3 pt-3 border-t border-stone-100">
                    <div className="text-xs text-stone-400 mb-1">Soil history</div>
                    {recs.length===0 ? <p className="text-xs text-stone-400">No recommendations yet</p> : (
                      <div className="space-y-1">
                        {recs.slice(0,3).map(r=>(
                          <div key={r.id} className="text-xs flex justify-between">
                            <span>{cropLabel(r.top_crops?.[0]?.crop)}</span>
                            <span className="text-stone-400">{new Date(r.created_at).toLocaleDateString()}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardBody>
              </Card>
            )
          })}
        </div>
      )}

      <Dialog open={open} onClose={()=>setOpen(false)} className="relative z-50">
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 space-y-4">
            <Dialog.Title className="font-bold text-lg">{editing?'Edit Field':'Add Field'}</Dialog.Title>
            <Input label="Name" value={form.name||''} onChange={e=>setForm(s=>({...s,name:e.target.value}))} placeholder="North paddock" />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Latitude" type="number" step="any" value={form.latitude ?? ''} onChange={e=>setForm(s=>({...s,latitude:e.target.value===''?null:parseFloat(e.target.value)}))} />
              <Input label="Longitude" type="number" step="any" value={form.longitude ?? ''} onChange={e=>setForm(s=>({...s,longitude:e.target.value===''?null:parseFloat(e.target.value)}))} />
            </div>
            <div>
              <div className="text-xs text-stone-500 mb-1">Pick on map (click to set lat/lon)</div>
              <div className="h-56 rounded-xl overflow-hidden border border-stone-200">
                <MapContainer center={[form.latitude ?? 28.6, form.longitude ?? 77.2]} zoom={form.latitude!=null?10:4} style={{height:'100%', width:'100%'}}>
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap' />
                  <FieldPicker lat={form.latitude ?? null} lon={form.longitude ?? null} onPick={(la,lo)=>setForm(s=>({...s,latitude:+la.toFixed(5), longitude:+lo.toFixed(5)}))} />
                </MapContainer>
              </div>
            </div>
            <Input label="Area (hectares)" type="number" step="0.1" value={form.area_hectares ?? ''} onChange={e=>setForm(s=>({...s,area_hectares:e.target.value===''?null:parseFloat(e.target.value)}))} />
            <div>
              <label className="text-sm font-medium text-stone-700 block mb-1">Soil type</label>
              <select value={form.soil_type||''} onChange={e=>setForm(s=>({...s,soil_type:e.target.value||null}))} className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm">
                <option value="">— Optional —</option>
                {SOIL_TYPES.map(s=><option key={s}>{s}</option>)}
              </select>
            </div>
            {formError && <div className="text-xs text-red-500 break-words">{formError}</div>}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="secondary" onClick={()=>setOpen(false)}>Cancel</Button>
              <Button onClick={save} disabled={saving}>{saving ? 'Saving…' : (editing?'Update':'Create')}</Button>
            </div>
          </Dialog.Panel>
        </div>
      </Dialog>

      <Dialog open={soilField!==null} onClose={()=>setSoilField(null)} className="relative z-50">
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 space-y-4">
            <Dialog.Title className="font-bold text-lg">Soil test — {soilField?.name}</Dialog.Title>
            <p className="text-xs text-stone-500">Enter NPK (kg/ha) and pH from your lab report. These pre-fill new recommendations for this field.</p>
            <div className="grid grid-cols-2 gap-3">
              <Input label="Nitrogen (N)" type="number" step="any" value={soilForm.soil_n ?? ''} onChange={e=>setSoilForm(s=>({...s,soil_n:num(e.target.value)}))} placeholder="e.g. 90" />
              <Input label="Phosphorus (P)" type="number" step="any" value={soilForm.soil_p ?? ''} onChange={e=>setSoilForm(s=>({...s,soil_p:num(e.target.value)}))} placeholder="e.g. 42" />
              <Input label="Potassium (K)" type="number" step="any" value={soilForm.soil_k ?? ''} onChange={e=>setSoilForm(s=>({...s,soil_k:num(e.target.value)}))} placeholder="e.g. 43" />
              <Input label="pH" type="number" step="0.1" value={soilForm.soil_ph ?? ''} onChange={e=>setSoilForm(s=>({...s,soil_ph:num(e.target.value)}))} placeholder="e.g. 6.5" />
            </div>
            {soilError && <div className="text-xs text-red-500 break-words">{soilError}</div>}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="secondary" onClick={()=>setSoilField(null)}>Cancel</Button>
              <Button onClick={saveSoilTest} disabled={soilSaving}>{soilSaving ? 'Saving…' : 'Save test'}</Button>
            </div>
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  )
}

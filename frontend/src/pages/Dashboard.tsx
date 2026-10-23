import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import 'leaflet/dist/leaflet.css'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import '@/hooks/useLeafletFix'
import { useAppStore } from '@/stores/appStore'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { CropThumb } from '@/components/ui/CropThumb'
import { cropLabel } from '@/utils/cropMeta'
import { formatDate } from '@/utils/helpers'

export default function Dashboard() {
  const { fields, history, fetchFields, fetchHistory } = useAppStore()
  useEffect(()=>{ fetchFields(); fetchHistory() }, [])

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <Link to="/recommend"><Button>✦ New Recommendation</Button></Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card><CardBody><div className="text-sm text-stone-500">Fields</div><div className="text-3xl font-bold mt-1">{fields.length}</div></CardBody></Card>
        <Card><CardBody><div className="text-sm text-stone-500">Recommendations</div><div className="text-3xl font-bold mt-1">{history.length}</div></CardBody></Card>
        <Card><CardBody><div className="text-sm text-stone-500">Feedback given</div><div className="text-3xl font-bold mt-1">{history.filter(h=>h.actual_crop).length}</div></CardBody></Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><h2 className="font-semibold">Your Fields</h2></CardHeader>
          <CardBody>
            {fields.length===0 ? (
              <div className="text-center py-8 text-stone-400">
                <div className="text-3xl mb-2">◈</div>
                <p className="text-sm">No fields yet</p>
                <Link to="/fields" className="text-sm text-brand-600 hover:underline mt-2 inline-block">Add your first field</Link>
              </div>
            ) : (
              <div className="space-y-2">
                {fields.slice(0,5).map(f=>(
                  <div key={f.id} className="flex items-center justify-between p-3 rounded-lg bg-stone-50 border border-stone-100">
                    <div>
                      <div className="font-medium text-sm">{f.name}</div>
                      <div className="text-xs text-stone-500">{f.soil_type || '—'} {f.area_hectares?`· ${f.area_hectares} ha`:''}</div>
                    </div>
                    <span className="text-xs text-stone-400">{f.latitude?.toFixed(2)}, {f.longitude?.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader><h2 className="font-semibold">Recent Recommendations</h2></CardHeader>
          <CardBody>
            {history.length===0 ? (
              <p className="text-sm text-stone-400 text-center py-8">No recommendations yet — <Link to="/recommend" className="text-brand-600 hover:underline">create one</Link></p>
            ) : (
              <div className="space-y-2">
                {history.slice(0,5).map(h=>(
                  <div key={h.id} className="flex items-center gap-3 p-3 rounded-lg bg-stone-50 border border-stone-100">
                    <CropThumb crop={h.top_crops?.[0]?.crop} className="w-9 h-9 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium">{cropLabel(h.top_crops?.[0]?.crop)} <span className="text-xs text-stone-400">{((h.top_crops?.[0]?.confidence||0)*100).toFixed(0)}%</span></div>
                      <div className="text-xs text-stone-500">N{h.N} P{h.P} K{h.K} · pH{h.ph} · {formatDate(h.created_at)}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {(() => {
        const located = fields.filter(f => f.latitude != null && f.longitude != null)
        if (located.length === 0) return null
        const first = located[0]
        return (
        <Card>
          <CardHeader><h2 className="font-semibold">Field Locations</h2></CardHeader>
          <CardBody>
            <div className="h-[360px] rounded-xl overflow-hidden border border-stone-200">
              <MapContainer center={[first.latitude!, first.longitude!]} zoom={8} style={{height:'100%', width:'100%'}}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap contributors' />
                {located.map(f=>(
                  <Marker key={f.id} position={[f.latitude!, f.longitude!]}>
                    <Popup><div className="text-sm font-medium">{f.name}</div><div className="text-xs text-stone-500">{f.soil_type || ''} {f.area_hectares?`· ${f.area_hectares} ha`:''}</div></Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>
            <div className="mt-3 grid gap-1.5">
              {located.map(f=>(
                <div key={f.id} className="text-xs flex justify-between p-2 bg-stone-50 rounded">
                  <span className="font-medium">{f.name}</span>
                  <a href={`https://www.openstreetmap.org/?mlat=${f.latitude}&mlon=${f.longitude}#map=14/${f.latitude}/${f.longitude}`} target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">{f.latitude?.toFixed(4)}, {f.longitude?.toFixed(4)} ↗</a>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
        )
      })()}
    </div>
  )
}

import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '@/stores/appStore'
import { Card, CardBody } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { CropThumb } from '@/components/ui/CropThumb'
import { cropLabel } from '@/utils/cropMeta'
import { formatDate, confidenceColor, confidenceLabel } from '@/utils/helpers'

type SortKey = 'date' | 'crop' | 'confidence' | 'ph'
type SortDir = 'asc' | 'desc'

const PAGE_SIZE = 10

export default function History() {
  const navigate = useNavigate()
  const { history, fields, loading, error, fetchHistory } = useAppStore()

  const [crop, setCrop] = useState('')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('date')
  const [sortDir, setSortDir] = useState<SortDir>('desc')
  const [page, setPage] = useState(0)

  useEffect(() => { fetchHistory() }, [fetchHistory])

  const fieldName = (id: number | null) => {
    if (id == null) return '—'
    return fields.find((f) => f.id === id)?.name || `Field #${id}`
  }

  const filtered = useMemo(() => {
    return history.filter((h) => {
      if (crop && !h.top_crops?.some((c) => c.crop === crop)) return false
      const t = new Date(h.created_at).getTime()
      if (from && t < new Date(from).getTime()) return false
      if (to && t > new Date(to).getTime() + 86400000) return false
      if (search) {
        const q = search.toLowerCase()
        const blob = `${h.top_crops?.map((c) => c.crop).join(' ')} ${fieldName(h.field_id)} ${h.actual_crop || ''}`.toLowerCase()
        if (!blob.includes(q)) return false
      }
      return true
    })
  }, [history, crop, from, to, search, fields])

  const sorted = useMemo(() => {
    const arr = [...filtered]
    arr.sort((a, b) => {
      let av: string | number = 0
      let bv: string | number = 0
      if (sortKey === 'date') { av = a.created_at; bv = b.created_at }
      else if (sortKey === 'crop') {
        av = a.top_crops?.[0]?.crop || ''
        bv = b.top_crops?.[0]?.crop || ''
      }
      else if (sortKey === 'confidence') {
        av = a.top_crops?.[0]?.confidence || 0
        bv = b.top_crops?.[0]?.confidence || 0
      }
      else if (sortKey === 'ph') { av = a.ph; bv = b.ph }
      if (av < bv) return sortDir === 'asc' ? -1 : 1
      if (av > bv) return sortDir === 'asc' ? 1 : -1
      return 0
    })
    return arr
  }, [filtered, sortKey, sortDir])

  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE))
  const pageData = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
  const crops = Array.from(new Set(history.flatMap((h) => h.top_crops?.map((c) => c.crop) || [])))

  const setSort = (k: SortKey) => {
    if (sortKey === k) setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    else { setSortKey(k); setSortDir(k === 'date' ? 'desc' : 'asc') }
  }
  const arrow = (k: SortKey) => sortKey === k ? (sortDir === 'asc' ? ' ▲' : ' ▼') : ''

  const rerun = (h: (typeof history)[number]) => {
    navigate('/recommend', { state: { fromHistory: h } })
  }

  if (loading && history.length === 0) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">History</h1>
        <Card><CardBody><div className="text-center py-12 text-stone-400">Loading history…</div></CardBody></Card>
      </div>
    )
  }
  if (error && history.length === 0) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">History</h1>
        <Card><CardBody>
          <div className="text-center py-10 text-red-500">
            <p>Couldn't load history: {error}</p>
            <button onClick={() => fetchHistory()} className="mt-3 text-sm text-brand-600 hover:underline">Retry</button>
          </div>
        </CardBody></Card>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">History</h1>
        <p className="text-sm text-stone-500 mt-1">Past recommendations — filter, sort, and re-run.</p>
      </div>

      <Card>
        <CardBody>
          <div className="flex flex-wrap gap-3 items-end">
            <div>
              <label className="text-sm font-medium text-stone-700 block mb-1">Crop</label>
              <select value={crop} onChange={(e) => { setCrop(e.target.value); setPage(0) }} className="rounded-lg border border-stone-300 px-3 py-2 text-sm bg-white">
                <option value="">All crops</option>
                {crops.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <Input label="From" type="date" value={from} onChange={(e) => { setFrom(e.target.value); setPage(0) }} />
            <Input label="To" type="date" value={to} onChange={(e) => { setTo(e.target.value); setPage(0) }} />
            <div className="flex-1 min-w-[180px]">
              <Input label="Search" type="search" placeholder="Crop, field, actual…" value={search} onChange={(e) => { setSearch(e.target.value); setPage(0) }} />
            </div>
            <Button variant="ghost" onClick={() => { setCrop(''); setFrom(''); setTo(''); setSearch(''); setPage(0) }}>Clear</Button>
            <div className="ml-auto text-sm text-stone-500 self-center">{sorted.length} of {history.length}</div>
          </div>
        </CardBody>
      </Card>

      {history.length === 0 ? (
        <Card><CardBody>
          <div className="text-center py-14 text-stone-400">
            <div className="text-4xl mb-3">≡</div>
            <p className="font-medium text-stone-600">No recommendations yet</p>
            <p className="text-sm mt-1">Create your first recommendation to see it here.</p>
            <Button className="mt-4" onClick={() => navigate('/recommend')}>✦ New Recommendation</Button>
          </div>
        </CardBody></Card>
      ) : sorted.length === 0 ? (
        <Card><CardBody>
          <div className="text-center py-10 text-stone-400">
            <p>No recommendations match your filter.</p>
            <Button variant="ghost" className="mt-2" onClick={() => { setCrop(''); setFrom(''); setTo(''); setSearch('') }}>Clear filters</Button>
          </div>
        </CardBody></Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-stone-50 text-left text-xs text-stone-500 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3 cursor-pointer select-none" onClick={() => setSort('date')}>Date{arrow('date')}</th>
                  <th className="px-4 py-3">Field</th>
                  <th className="px-4 py-3 cursor-pointer select-none" onClick={() => setSort('crop')}>Top crop{arrow('crop')}</th>
                  <th className="px-4 py-3">N / P / K</th>
                  <th className="px-4 py-3 cursor-pointer select-none" onClick={() => setSort('ph')}>pH{arrow('ph')}</th>
                  <th className="px-4 py-3 cursor-pointer select-none" onClick={() => setSort('confidence')}>Confidence{arrow('confidence')}</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {pageData.map((h) => {
                  const top = h.top_crops?.[0]
                  const conf = top?.confidence || 0
                  return (
                    <tr key={h.id} onClick={() => navigate('/result', { state: { fromHistory: h } })} className="border-t border-stone-100 hover:bg-stone-50 cursor-pointer">
                      <td className="px-4 py-3 text-stone-500 whitespace-nowrap">{formatDate(h.created_at)}</td>
                      <td className="px-4 py-3 text-stone-700 max-w-[140px] truncate">{fieldName(h.field_id)}</td>
                      <td className="px-4 py-3">
                        <CropThumb crop={top?.crop} className="w-7 h-7 mr-1.5 align-middle" />
                        <span>{cropLabel(top?.crop)}</span>
                      </td>
                      <td className="px-4 py-3 text-stone-500 tabular-nums">{h.N} / {h.P} / {h.K}</td>
                      <td className="px-4 py-3 text-stone-500 tabular-nums">{h.ph.toFixed(1)}</td>
                      <td className="px-4 py-3">
                        <Badge className={confidenceColor(conf)}>{(conf * 100).toFixed(0)}% · {confidenceLabel(conf)}</Badge>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex gap-1 justify-end" onClick={(e) => e.stopPropagation()}>
                          <Button size="sm" variant="ghost" onClick={() => navigate('/result', { state: { fromHistory: h } })}>View</Button>
                          <Button size="sm" variant="secondary" onClick={() => rerun(h)}>Re-run</Button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between p-3 border-t border-stone-100 text-sm">
            <span className="text-stone-500">Page {page + 1} of {totalPages} · {PAGE_SIZE} per page</span>
            <div className="flex gap-2">
              <Button size="sm" variant="secondary" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>← Prev</Button>
              <Button size="sm" variant="secondary" disabled={page + 1 >= totalPages} onClick={() => setPage((p) => p + 1)}>Next →</Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

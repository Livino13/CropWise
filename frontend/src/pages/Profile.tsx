import { useEffect, useMemo, useState } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend,
} from 'chart.js'
import { useAppStore } from '@/stores/appStore'
import { api } from '@/api/client'
import type { HistoryEntry } from '@/api/types'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { CropThumb } from '@/components/ui/CropThumb'
import { cropLabel } from '@/utils/cropMeta'
import { formatDate } from '@/utils/helpers'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

type FB = { id: number; predicted: string; actual: string | null; yield: number | null; date: string; rating: number | null }

function pickFeedback(history: HistoryEntry[]): FB[] {
  return history
    .filter((h) => h.actual_crop)
    .map((h) => ({
      id: h.id,
      predicted: h.top_crops?.[0]?.crop || '—',
      actual: h.actual_crop ?? null,
      yield: h.actual_yield ?? null,
      date: h.created_at,
      rating: h.feedback_rating ?? null,
    }))
}

export default function Profile() {
  const { history, loading, error, fetchHistory } = useAppStore()

  const [selected, setSelected] = useState<number | ''>('')
  const [actualCrop, setActualCrop] = useState('')
  const [actualYield, setActualYield] = useState<number | ''>('')
  const [rating, setRating] = useState(0)
  const [hoverRating, setHoverRating] = useState(0)
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState<{ kind: 'ok' | 'err'; text: string } | null>(null)

  useEffect(() => { fetchHistory() }, [fetchHistory])

  const feedback = useMemo(() => pickFeedback(history), [history])
  const yields = feedback.map((f) => f.yield || 0).filter((y) => y > 0)
  const avgYield = yields.length ? yields.reduce((a, b) => a + b, 0) / yields.length : 0
  const matchRate = feedback.length
    ? feedback.filter((f) => f.predicted === f.actual).length / feedback.length
    : 0

  const submit = async () => {
    if (!selected) { setMsg({ kind: 'err', text: 'Select a recommendation first.' }); return }
    setSaving(true); setMsg(null)
    try {
      await api.feedback({
        recommendation_id: Number(selected),
        actual_crop: actualCrop.trim() || undefined,
        actual_yield: actualYield === '' ? undefined : Number(actualYield),
        rating: rating || undefined,
        notes: notes.trim() || undefined,
      })
      setMsg({ kind: 'ok', text: 'Saved. Thanks for the feedback!' })
      setSelected(''); setActualCrop(''); setActualYield(''); setRating(0); setNotes('')
      await fetchHistory()
    } catch (e: unknown) {
      setMsg({ kind: 'err', text: 'Failed: ' + (e instanceof Error ? e.message : String(e)) })
    } finally { setSaving(false) }
  }

  const yieldChart = {
    labels: feedback.map((f) => formatDate(f.date)),
    datasets: [
      { label: 'Actual yield (t/ha)', data: feedback.map((f) => f.yield ?? 0), borderColor: '#16a34a', backgroundColor: '#dcfce7', tension: 0.25, fill: true },
    ],
  }
  const yieldOpts = { responsive: true, plugins: { legend: { display: true } }, scales: { y: { beginAtZero: true } } }

  if (loading && history.length === 0) {
    return (
      <div className="max-w-5xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">Profile & Feedback</h1>
        <Card><CardBody><div className="text-center py-12 text-stone-400">Loading…</div></CardBody></Card>
      </div>
    )
  }
  if (error && history.length === 0) {
    return (
      <div className="max-w-5xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">Profile & Feedback</h1>
        <Card><CardBody>
          <div className="text-center py-10 text-red-500">
            <p>Couldn't load: {error}</p>
            <button onClick={() => fetchHistory()} className="mt-3 text-sm text-brand-600 hover:underline">Retry</button>
          </div>
        </CardBody></Card>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Profile & Feedback</h1>
        <p className="text-sm text-stone-500 mt-1">Track what you actually planted, the yield you got, and how the model did.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card><CardBody>
          <div className="text-xs text-stone-500 uppercase tracking-wide">Total recs</div>
          <div className="text-3xl font-bold text-brand-700 mt-1">{history.length}</div>
        </CardBody></Card>
        <Card><CardBody>
          <div className="text-xs text-stone-500 uppercase tracking-wide">Feedback given</div>
          <div className="text-3xl font-bold text-brand-700 mt-1">{feedback.length}</div>
          {history.length > 0 && <div className="text-xs text-stone-400 mt-1">{Math.round((feedback.length / history.length) * 100)}% of total</div>}
        </CardBody></Card>
        <Card><CardBody>
          <div className="text-xs text-stone-500 uppercase tracking-wide">Avg yield</div>
          <div className="text-3xl font-bold text-brand-700 mt-1">{avgYield ? `${avgYield.toFixed(1)}` : '—'}</div>
          {avgYield > 0 && <div className="text-xs text-stone-400 mt-1">t/ha across {yields.length} harvests</div>}
        </CardBody></Card>
        <Card><CardBody>
          <div className="text-xs text-stone-500 uppercase tracking-wide">Crop match</div>
          <div className="text-3xl font-bold text-brand-700 mt-1">{feedback.length ? `${(matchRate * 100).toFixed(0)}%` : '—'}</div>
          {feedback.length > 0 && <div className="text-xs text-stone-400 mt-1">predicted = planted</div>}
        </CardBody></Card>
      </div>

      <Card>
        <CardHeader>
          <h2 className="font-semibold">Submit feedback</h2>
          <p className="text-xs text-stone-500 mt-0.5">Record what you actually grew and how it turned out.</p>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-stone-700 block mb-1">Past recommendation</label>
              <select
                value={selected}
                onChange={(e) => setSelected(e.target.value ? Number(e.target.value) : '')}
                className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm bg-white"
              >
                <option value="">Select a past recommendation…</option>
                {history.slice(0, 50).map((h) => (
                  <option key={h.id} value={h.id}>
                    #{h.id} · {formatDate(h.created_at)} · {h.top_crops?.[0]?.crop}
                    {h.actual_crop ? ' (feedback given)' : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Input label="Actual crop planted" value={actualCrop} onChange={(e) => setActualCrop(e.target.value)} placeholder="e.g. wheat" />
              <Input
                label="Actual yield (t/ha)"
                type="number" step="0.1" min="0"
                value={actualYield}
                onChange={(e) => setActualYield(e.target.value === '' ? '' : parseFloat(e.target.value))}
                placeholder="e.g. 3.2"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-stone-700 block mb-1">Rating</label>
              <div className="flex items-center gap-1" onMouseLeave={() => setHoverRating(0)}>
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n} type="button"
                    onClick={() => setRating(n)}
                    onMouseEnter={() => setHoverRating(n)}
                    aria-label={`${n} star${n > 1 ? 's' : ''}`}
                    className={`text-2xl transition leading-none ${(hoverRating || rating) >= n ? 'text-amber-400' : 'text-stone-300 hover:text-amber-300'}`}
                  >★</button>
                ))}
                <span className="text-xs text-stone-400 ml-2">{rating ? `${rating} / 5` : 'Tap a star'}</span>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-stone-700 block mb-1">Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
                placeholder="Observations, pest issues, weather anomalies…"
              />
            </div>

            <div className="flex items-center justify-between pt-1">
              {msg ? (
                <span className={`text-sm ${msg.kind === 'ok' ? 'text-green-600' : 'text-red-500'}`}>{msg.text}</span>
              ) : <span className="text-sm text-stone-400">Feedback improves future recommendations.</span>}
              <Button onClick={submit} disabled={saving || !selected}>{saving ? 'Saving…' : 'Save feedback'}</Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {feedback.length > 0 && (
        <>
          <Card>
            <CardHeader>
              <h2 className="font-semibold">Yield history</h2>
              <p className="text-xs text-stone-500 mt-0.5">Track your harvest over time.</p>
            </CardHeader>
            <CardBody>
              <Line data={yieldChart} options={yieldOpts} />
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h2 className="font-semibold">Predicted vs actual</h2>
              <p className="text-xs text-stone-500 mt-0.5">Where the model agreed with what you planted.</p>
            </CardHeader>
            <CardBody>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-xs text-stone-500 uppercase tracking-wider text-left">
                    <tr className="bg-stone-50">
                      <th className="px-3 py-2">Date</th>
                      <th className="px-3 py-2">Predicted</th>
                      <th className="px-3 py-2">Actual</th>
                      <th className="px-3 py-2">Match</th>
                      <th className="px-3 py-2">Yield</th>
                      <th className="px-3 py-2">Rating</th>
                    </tr>
                  </thead>
                  <tbody>
                    {feedback.map((f) => {
                      const match = f.predicted && f.actual && f.predicted === f.actual
                      return (
                        <tr key={f.id} className="border-t border-stone-100">
                          <td className="px-3 py-2 text-stone-500 whitespace-nowrap">{formatDate(f.date)}</td>
                          <td className="px-3 py-2"><CropThumb crop={f.predicted} className="w-6 h-6 mr-1.5 align-middle" /><span>{cropLabel(f.predicted)}</span></td>
                          <td className="px-3 py-2"><CropThumb crop={f.actual || undefined} className="w-6 h-6 mr-1.5 align-middle" /><span>{cropLabel(f.actual)}</span></td>
                          <td className="px-3 py-2">
                            <Badge color={match ? 'green' : 'amber'}>{match ? 'match' : 'differ'}</Badge>
                          </td>
                          <td className="px-3 py-2 tabular-nums">{f.yield != null ? `${f.yield} t/ha` : '—'}</td>
                          <td className="px-3 py-2 text-amber-400">{f.rating ? '★'.repeat(f.rating) + '☆'.repeat(5 - f.rating) : '—'}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </CardBody>
          </Card>
        </>
      )}

      {history.length > 0 && feedback.length === 0 && (
        <Card><CardBody>
          <div className="text-center py-8 text-stone-400">
            <div className="text-3xl mb-2">★</div>
            <p className="text-sm">No feedback yet — use the form above to record what you actually grew.</p>
          </div>
        </CardBody></Card>
      )}
    </div>
  )
}

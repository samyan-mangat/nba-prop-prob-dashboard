import React, { useEffect, useState } from 'react'
import { api } from '../lib/api'
import type { IngestTask } from '../lib/api'

const SEASONS = [
  '2018-19','2019-20','2020-21','2021-22','2022-23','2023-24','2024-25'
]

export default function SeasonIngestPanel() {
  const [checked, setChecked] = useState<string[]>(['2023-24'])
  const [start, setStart] = useState<string>('')  // YYYY-MM-DD (optional)
  const [end, setEnd] = useState<string>('')
  const [playersOnly, setPlayersOnly] = useState(false)
  const [task, setTask] = useState<IngestTask | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const toggle = (s: string) =>
    setChecked(prev => prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s])

  const startIngest = async () => {
    if (!playersOnly && checked.length === 0) return alert('Pick at least one season')
    setLoading(true); setError(null)
    try {
      const body: any = { seasons: checked, players_only: playersOnly }
      if (start) body.start_date = start
      if (end) body.end_date = end
      const { data } = await api.post<IngestTask>('/admin/ingest', body)
      setTask(data)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Start failed')
    } finally {
      setLoading(false)
    }
  }

  // poll task
  useEffect(() => {
    if (!task || (task.status === 'done' || task.status === 'error')) return
    const id = setInterval(async () => {
      try {
        const { data } = await api.get<IngestTask>(`/admin/tasks/${task.id}`)
        setTask(data)
      } catch {}
    }, 1500)
    return () => clearInterval(id)
  }, [task])

  return (
    <div className="bg-white shadow rounded-2xl p-4 space-y-3">
      <div className="font-semibold text-lg">Data Ingestion (dev)</div>

      <div className="flex flex-wrap gap-3">
        {SEASONS.map(s => (
          <label key={s} className="inline-flex items-center gap-2">
            <input type="checkbox" checked={checked.includes(s)} onChange={() => toggle(s)} />
            <span className="text-sm">{s}</span>
          </label>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <div className="text-xs text-gray-600 mb-1">Start date (optional)</div>
          <input type="date" value={start} onChange={e => setStart(e.target.value)} className="border rounded px-2 py-1 w-full" />
        </div>
        <div>
          <div className="text-xs text-gray-600 mb-1">End date (optional)</div>
          <input type="date" value={end} onChange={e => setEnd(e.target.value)} className="border rounded px-2 py-1 w-full" />
        </div>
        <label className="flex items-end gap-2">
          <input type="checkbox" checked={playersOnly} onChange={e => setPlayersOnly(e.target.checked)} />
          <span className="text-sm">Players only</span>
        </label>
      </div>

      <div className="flex gap-2">
        <button onClick={startIngest} className="bg-blue-600 text-white rounded px-3 py-2" disabled={loading}>
          {loading ? 'Starting…' : 'Ingest Selected'}
        </button>
      </div>

      {error && <div className="p-2 text-sm text-red-700 bg-red-50 rounded">{error}</div>}
      {task && (
        <div className="text-sm">
          <div>ID: <code>{task.id}</code></div>
          <div>Status: <b>{task.status}</b> — {task.message}</div>
          <div className="h-2 bg-gray-200 rounded mt-1">
            <div className="h-2 bg-green-500 rounded" style={{ width: `${Math.round(task.progress * 100)}%` }}></div>
          </div>
          {task.status === 'done' && <div className="text-green-700 mt-1">Rows inserted: {task.result_rows}</div>}
          {task.status === 'error' && <div className="text-red-700 mt-1">Failed.</div>}
        </div>
      )}
    </div>
  )
}

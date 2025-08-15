import React, { useEffect, useRef, useState } from 'react'
import { api } from '../lib/api'
import type { Player } from '../lib/api'

type Props = {
  onSelect: (p: Player) => void
  placeholder?: string
  limit?: number
  className?: string
  recentKey?: string
  autoFocus?: boolean
}

export default function PlayerSearch({
  onSelect,
  placeholder = 'Search player…',
  limit = 8,
  className = '',
  recentKey = 'recentPlayers',
  autoFocus = false,
}: Props) {
  const [q, setQ] = useState('')
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<Player[]>([])
  const [hi, setHi] = useState(-1) // highlighted index
  const [recent, setRecent] = useState<Player[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const boxRef = useRef<HTMLDivElement>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const lastQRef = useRef('')

  // Load recent from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(recentKey)
      if (raw) setRecent(JSON.parse(raw))
    } catch {}
  }, [recentKey])

  // Click outside to close
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (!boxRef.current?.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    if (!q || q.trim().length < 2) {
      setResults([])
      setError(null)
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    debounceRef.current = setTimeout(async () => {
      const thisQ = q.trim()
      lastQRef.current = thisQ
      try {
        const { data } = await api.get<Player[]>('/players/search', {
          params: { q: thisQ, limit },
        })
        // Only set if still the current query
        if (lastQRef.current === thisQ) setResults(data || [])
      } catch (e: any) {
        if (lastQRef.current === thisQ) setError(e?.message || 'Search failed')
      } finally {
        if (lastQRef.current === thisQ) setLoading(false)
      }
    }, 250)
  }, [q, limit])

  const select = (p: Player) => {
    onSelect(p)
    setQ(p.full_name)
    setOpen(false)
    // update recent (unique by id, max 10)
    try {
      const arr = [p, ...recent.filter(r => r.id !== p.id)].slice(0, 10)
      setRecent(arr)
      localStorage.setItem(recentKey, JSON.stringify(arr))
    } catch {}
  }

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    const list = (results.length > 0 ? results : recent)
    if (!open && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) setOpen(true)
    if (!open || list.length === 0) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setHi(h => (h + 1) % list.length)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setHi(h => (h - 1 + list.length) % list.length)
    } else if (e.key === 'Enter') {
      e.preventDefault()
      const idx = hi >= 0 ? hi : 0
      if (list[idx]) select(list[idx])
    } else if (e.key === 'Escape') {
      setOpen(false)
    }
  }

  const list = results.length > 0 ? results : recent

  return (
    <div className={`relative ${className}`} ref={boxRef}>
      <input
        ref={inputRef}
        value={q}
        onChange={(e) => { setQ(e.target.value); setOpen(true); setHi(-1) }}
        onFocus={() => setOpen(true)}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className="w-full border rounded px-3 py-2"
      />
      {open && (
        <div className="absolute z-20 mt-1 w-full bg-white border rounded shadow max-h-80 overflow-auto">
          {loading && <div className="px-3 py-2 text-sm text-gray-500">Searching…</div>}
          {error && <div className="px-3 py-2 text-sm text-red-600">{error}</div>}
          {!loading && !error && list.length === 0 && (
            <div className="px-3 py-2 text-sm text-gray-500">No results</div>
          )}
          {!loading && !error && list.length > 0 && (
            <ul>
              {list.map((p, i) => (
                <li
                  key={p.id}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => select(p)}
                  onMouseEnter={() => setHi(i)}
                  className={`px-3 py-2 cursor-pointer ${i === hi ? 'bg-blue-50' : ''}`}
                >
                  <div className="text-sm font-medium">{p.full_name}</div>
                  <div className="text-xs text-gray-500">
                    ID {p.id}{p.team_abbrev ? ` • ${p.team_abbrev}` : ''}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

import React, { useState } from 'react'
import { api, PropLeg } from '../lib/api'
import ProbabilityCard from './ProbabilityCard'
import Heatmap from './Heatmap'
import PlayerSearch from './PlayerSearch'
import type { Player } from '../lib/api'

export default function ParlayBuilder() {
  const [legs, setLegs] = useState<PropLeg[]>([])
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null)
  const [prop, setProp] = useState<PropLeg['prop']>('pts')
  const [threshold, setThreshold] = useState<number>(25)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addLeg = () => {
    if (!selectedPlayer) return alert('Pick a player first')
    setLegs([...legs, { player_id: selectedPlayer.id, prop, threshold }])
  }

  const compute = async () => {
    if (legs.length === 0) {
      alert('Add at least one leg first (click "Add Leg").')
      return
    }
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      if (legs.length === 1) {
        const { data } = await api.post('/props/probability', { leg: legs[0] })
        setResult({ type: 'single', data })
      } else {
        const { data } = await api.post('/props/sgp', { legs })
        setResult({ type: 'sgp', data })
      }
    } catch (e: any) {
      console.error('Compute error:', e)
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        'Request failed. Is the API running on http://localhost:8000 and was data ingested?'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white shadow rounded-2xl p-4 space-y-4">
      <div className="font-semibold text-lg">Parlay Builder</div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="text-xs text-gray-600 mb-1">Player</div>
          <PlayerSearch
            onSelect={(p) => setSelectedPlayer(p)}
            placeholder="Type to search (e.g., tatum)…"
            limit={8}
          />
          {selectedPlayer && (
            <div className="mt-1 text-xs text-gray-600">
              Selected: <span className="font-medium">{selectedPlayer.full_name}</span> (ID {selectedPlayer.id}{selectedPlayer.team_abbrev ? `, ${selectedPlayer.team_abbrev}` : ''})
              <button
                onClick={() => setSelectedPlayer(null)}
                className="ml-2 text-blue-600 hover:underline"
              >
                Change
              </button>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-2 content-start">
          <div>
            <div className="text-xs text-gray-600 mb-1">Prop</div>
            <select className="border rounded px-2 py-1 w-full" value={prop} onChange={(e) => setProp(e.target.value as any)}>
              {['pts','reb','ast','stl','blk','tov','fg3m'].map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div>
            <div className="text-xs text-gray-600 mb-1">Threshold</div>
            <input
              type="number"
              className="border rounded px-2 py-1 w-full"
              value={Number.isNaN(threshold) ? '' : threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value || '0'))}
            />
          </div>
          <div className="col-span-2 flex gap-2">
            <button onClick={addLeg} className="bg-blue-600 text-white rounded px-3 py-1" disabled={loading}>
              Add Leg
            </button>
            <button
              onClick={() => { setLegs([]); setResult(null); setError(null); }}
              className="bg-gray-200 rounded px-3 py-1"
              disabled={loading}
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      <div className="text-sm text-gray-600">Current Legs: {legs.map((l,i) => `${l.player_id}:${l.prop}≥${l.threshold}`).join(' | ') || 'none'}</div>

      <div className="flex gap-2">
        <button onClick={compute} className="bg-green-600 text-white rounded px-3 py-1" disabled={loading}>
          {loading ? 'Computing…' : 'Compute'}
        </button>
      </div>

      {error && <div className="p-3 bg-red-50 text-red-700 rounded text-sm">{error}</div>}

      {result && result.type === 'single' && (
        <ProbabilityCard title="Single Leg Probability" value={result.data.probability} subtitle={`n=${result.data.sample_size}`} />
      )}

      {result && result.type === 'sgp' && (
        <div className="space-y-4">
          <ProbabilityCard title="Joint Probability" value={result.data.joint_probability} subtitle={`sample_size=${result.data.sample_size}`} />
          <div className="grid grid-cols-3 gap-2">
            {result.data.per_leg.map((pl:any, idx:number) => (
              <ProbabilityCard key={idx} title={`Leg ${idx+1}`} value={pl.marginal} subtitle={`th≥${pl.threshold}`} />
            ))}
          </div>
          <Heatmap matrix={result.data.kendall_tau} labels={legs.map(l => l.prop)} />
        </div>
      )}
    </div>
  )
}

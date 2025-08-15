import React, { useState } from 'react'
import { api } from '../lib/api'

export default function Chat() {
  const [q, setQ] = useState('Tatum 30+ pts and 8+ reb on 2023-10-30')
  const [answer, setAnswer] = useState<string>('')
  const [raw, setRaw] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const send = async () => {
    setLoading(true)
    setError(null)
    setAnswer('')
    setRaw(null)
    try {
      const { data } = await api.post('/chat/ask', { query: q })
      setAnswer(data.answer)
      setRaw(data)
    } catch (e: any) {
      console.error('Chat error:', e)
      setError(e?.response?.data?.detail || e?.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white shadow rounded-2xl p-4 space-y-3">
      <div className="font-semibold text-lg">Parlay Chat</div>
      <div className="flex gap-2">
        <input
          value={q}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQ(e.target.value)}
          className="flex-1 border rounded px-3 py-2"
          placeholder="Ask about props..."
        />
        <button onClick={send} className="bg-blue-600 text-white rounded px-3 py-2" disabled={loading}>
          {loading ? 'Asking…' : 'Ask'}
        </button>
      </div>
      {error && <div className="p-3 bg-red-50 text-red-700 rounded text-sm">{error}</div>}
      {answer && <div className="p-3 bg-gray-50 rounded">{answer}</div>}
      {raw && (
        <details>
          <summary className="cursor-pointer text-sm text-gray-600">Details</summary>
          <pre className="text-xs overflow-auto">{JSON.stringify(raw, null, 2)}</pre>
        </details>
      )}
    </div>
  )
}

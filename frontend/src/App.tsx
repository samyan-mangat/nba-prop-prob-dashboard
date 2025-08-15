import React from 'react'
import ParlayBuilder from './components/ParlayBuilder'
import Chat from './components/Chat'
import SeasonIngestPanel from './components/SeasonIngestPanel'

export default function App() {
  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">NBA Player Prop Probability Dashboard</h1>
      <div className="grid md:grid-cols-2 gap-6">
        <ParlayBuilder />
        <Chat />
      </div>
      {/* Dev utility: Ingest seasons from the UI */}
      <SeasonIngestPanel />
      <p className="text-xs text-gray-500">Educational use only. Not affiliated with the NBA.</p>
    </div>
  )
}

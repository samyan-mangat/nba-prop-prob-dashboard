import React from 'react'

type Props = { matrix: number[][]; labels: string[] }
export default function Heatmap({ matrix, labels }: Props) {
  return (
    <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${labels.length + 1}, minmax(0,1fr))` }}>
      <div></div>
      {labels.map((l) => (
        <div key={'h' + l} className="text-xs text-center text-gray-600">{l}</div>
      ))}
      {matrix.map((row, i) => (
        <React.Fragment key={i}>
          <div className="text-xs text-right pr-1 text-gray-600">{labels[i]}</div>
          {row.map((v, j) => (
            <div key={i + ':' + j} className="h-8 flex items-center justify-center rounded" style={{ background: `rgba(59,130,246,${Math.min(1, Math.abs(v))})` }}>
              <span className="text-xs text-white">{v.toFixed(2)}</span>
            </div>
          ))}
        </React.Fragment>
      ))}
    </div>
  )
}
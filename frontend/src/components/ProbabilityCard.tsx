import React from 'react'

type Props = { title: string; value: number; subtitle?: string }
export default function ProbabilityCard({ title, value, subtitle }: Props) {
  return (
    <div className="bg-white shadow rounded-2xl p-4">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-3xl font-semibold">{(value * 100).toFixed(1)}%</div>
      {subtitle && <div className="text-xs text-gray-400 mt-1">{subtitle}</div>}
    </div>
  )
}
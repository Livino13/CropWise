import React from 'react'
export function Badge({ children, color='green', className='' }: { children: React.ReactNode; color?: 'green'|'amber'|'red'|'stone'|'blue'|string; className?: string }) {
  const map: Record<string,string> = {
    green:'bg-green-100 text-green-700 border-green-200',
    amber:'bg-amber-100 text-amber-700 border-amber-200',
    red:'bg-red-100 text-red-700 border-red-200',
    stone:'bg-stone-100 text-stone-600 border-stone-200',
    blue:'bg-blue-100 text-blue-700 border-blue-200',
  }
  return <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${map[color]||map.stone} ${className}`}>{children}</span>
}
export default Badge

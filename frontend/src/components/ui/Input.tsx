import React from 'react'
type Props = React.InputHTMLAttributes<HTMLInputElement> & { label?: string; error?: string }
export function Input({ label, error, id, ...p}: Props) {
  const autoId = React.useId()
  const inputId = id ?? autoId
  return (
    <label className="block" htmlFor={inputId}>
      {label && <span className="text-sm font-medium text-stone-700 mb-1 block">{label}</span>}
      <input id={inputId} className={`w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 placeholder:text-stone-400 ${error?'border-red-400':'border-stone-300'}`} aria-invalid={!!error} aria-describedby={error?`${inputId}-err`:undefined} {...p} />
      {error && <span id={`${inputId}-err`} className="text-xs text-red-500 mt-1 block">{error}</span>}
    </label>
  )
}
export default Input

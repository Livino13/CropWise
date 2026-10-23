import React from 'react'
const variants: Record<string,string> = {
  primary: 'bg-brand-600 text-white hover:bg-brand-700 shadow-sm',
  secondary: 'bg-white text-stone-700 hover:bg-stone-50 border border-stone-200',
  ghost: 'text-stone-600 hover:bg-stone-100',
}
const sizes: Record<string,string> = { sm:'px-3 py-1.5 text-sm', md:'px-4 py-2 text-sm', lg:'px-6 py-3 text-base' }
export function Button({ variant='primary', size='md', className='', ...p}: React.ButtonHTMLAttributes<HTMLButtonElement>&{variant?: 'primary'|'secondary'|'ghost'; size?: 'sm'|'md'|'lg'}) {
  const v = variants[variant] ?? variants.primary
  const s = sizes[size] ?? sizes.md
  return <button className={`inline-flex items-center justify-center rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${v} ${s} ${className}`} {...p} />
}
export default Button

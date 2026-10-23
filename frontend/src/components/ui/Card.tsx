import React from 'react'
export function Card({ className='', children, ...p}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={`bg-white rounded-xl border border-stone-200 shadow-sm ${className}`} {...p}>{children}</div>
}
export function CardHeader({ className='', ...p}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={`px-5 py-4 border-b border-stone-100 ${className}`} {...p} />
}
export function CardBody({ className='', ...p}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={`px-5 py-4 ${className}`} {...p} />
}
export function CardFooter({ className='', ...p}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={`px-5 py-3 border-t border-stone-100 bg-stone-50 rounded-b-xl ${className}`} {...p} />
}

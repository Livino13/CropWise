import { NavLink, Outlet } from 'react-router-dom'
import { useState, useRef, useEffect } from 'react'
import { useAppStore } from '@/stores/appStore'
import { ChatWidget } from '@/components/ChatWidget'

const NAV = [
  { to: '/', label: 'Dashboard', icon: '▦' },
  { to: '/recommend', label: 'New Recommendation', icon: '✦' },
  { to: '/fields', label: 'Fields', icon: '◈' },
  { to: '/history', label: 'History', icon: '≡' },
  { to: '/guide', label: 'Crop Guide', icon: '◫' },
  { to: '/profile', label: 'Profile', icon: '◐' },
]

function initials(name: string) {
  return name.split(/\s+/).map((p) => p[0]).filter(Boolean).slice(0, 2).join('').toUpperCase()
}

export function Layout() {
  const [open, setOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const user = useAppStore((s) => s.user)
  const signOut = useAppStore((s) => s.signOut)

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  return (
    <div className="min-h-screen flex">
      <aside className={`${open?'translate-x-0':'-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-30 w-64 bg-white border-r border-stone-200 flex flex-col transition-transform`}>
        <div className="px-6 py-5 flex items-center gap-3 border-b border-stone-100">
          <span className="w-9 h-9 rounded-xl bg-brand-600 text-white grid place-items-center font-bold">C</span>
          <span className="font-bold text-lg tracking-tight">CropWise</span>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-auto" aria-label="Primary">
          {NAV.map(n=>(
            <NavLink key={n.to} to={n.to} end={n.to==='/' } onClick={()=>setOpen(false)}
              className={({isActive})=>`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive?'bg-brand-50 text-brand-700':'text-stone-600 hover:bg-stone-50'}`}>
              <span className="w-5 text-center" aria-hidden>{n.icon}</span>{n.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 text-xs text-stone-400 border-t border-stone-100">Practical crop guidance</div>
      </aside>
      {open && <div className="fixed inset-0 bg-black/20 z-20 lg:hidden" onClick={()=>setOpen(false)} aria-hidden />}

      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar — always visible on desktop, compact on mobile with hamburger */}
        <header className="h-14 bg-white border-b border-stone-200 flex items-center px-4 gap-3 shrink-0">
          <button onClick={()=>setOpen(!open)} className="lg:hidden p-2 rounded-lg hover:bg-stone-100" aria-label="Toggle navigation">☰</button>
          <span className="font-bold tracking-tight text-brand-700">CropWise</span>
          <span className="hidden sm:inline text-xs text-stone-400 ml-2">Smart crop recommendations</span>

          {user && (
            <div className="ml-auto relative" ref={menuRef}>
              <button
                onClick={() => setMenuOpen((v) => !v)}
                className="flex items-center gap-2 rounded-full hover:bg-stone-50 p-1 pr-3 transition-colors"
                aria-haspopup="menu"
                aria-expanded={menuOpen}
              >
                {user.picture ? (
                  <img src={user.picture} alt="" className="w-7 h-7 rounded-full object-cover" />
                ) : (
                  <span className="w-7 h-7 rounded-full bg-brand-600 text-white text-xs font-semibold grid place-items-center">{initials(user.name)}</span>
                )}
                <span className="hidden sm:inline text-sm text-stone-700 max-w-[140px] truncate">{user.name}</span>
              </button>
              {menuOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl border border-stone-200 shadow-lg py-1 z-40">
                  <div className="px-3 py-2 border-b border-stone-100">
                    <div className="text-sm font-medium text-stone-800 truncate">{user.name}</div>
                    <div className="text-xs text-stone-500 truncate">{user.email}</div>
                  </div>
                  <button
                    onClick={() => { setMenuOpen(false); signOut() }}
                    className="w-full text-left px-3 py-2 text-sm text-stone-700 hover:bg-stone-50"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          )}
        </header>
        <main className="flex-1 p-4 lg:p-6 bg-stone-50 overflow-auto">
          <Outlet />
        </main>
      </div>
      <ChatWidget />
    </div>
  )
}
export default Layout

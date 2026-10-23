import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppStore } from '@/stores/appStore'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const user = useAppStore((s) => s.user)
  const signInWithGoogle = useAppStore((s) => s.signInWithGoogle)
  const [loading, setLoading] = useState(false)
  const from = (location.state as { from?: string } | null)?.from ?? '/'

  useEffect(() => { if (user) navigate(from, { replace: true }) }, [user, from, navigate])

  const handleGoogle = async () => {
    setLoading(true)
    try { await signInWithGoogle() } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-stone-50 via-emerald-50/40 to-amber-50/30 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-600 text-white text-2xl font-bold shadow-md">C</div>
          <h1 className="mt-4 text-2xl font-bold tracking-tight text-stone-800">CropWise</h1>
          <p className="text-sm text-stone-500 mt-1">Smart crop recommendations for your soil and climate.</p>
        </div>

        <div className="bg-white rounded-2xl border border-stone-200 shadow-sm p-6 space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-stone-800">Sign in to continue</h2>
            <p className="text-sm text-stone-500 mt-1">We'll save your field history and recommendations across devices.</p>
          </div>

          <button
            onClick={handleGoogle}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl border border-stone-300 bg-white hover:bg-stone-50 active:bg-stone-100 transition-colors text-sm font-medium text-stone-700 disabled:opacity-60 disabled:cursor-not-allowed"
            aria-label="Continue with Google"
          >
            {loading ? (
              <span className="inline-block w-4 h-4 border-2 border-stone-300 border-t-brand-600 rounded-full animate-spin" aria-hidden />
            ) : (
              <GoogleLogo />
            )}
            <span>{loading ? 'Signing in…' : 'Continue with Google'}</span>
          </button>

          <p className="text-xs text-stone-400 text-center">
            By continuing you agree to CropWise's Terms and Privacy Policy.
          </p>
        </div>

        <p className="text-center text-xs text-stone-400 mt-6">
          New to CropWise? Sign in with Google to create your account.
        </p>
      </div>
    </div>
  )
}

function GoogleLogo() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden>
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A10.99 10.99 0 0 0 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18A10.99 10.99 0 0 0 1 12c0 1.77.42 3.45 1.18 4.93l3.66-2.84z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38z"/>
    </svg>
  )
}

import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { useAppStore } from '@/stores/appStore'
import Dashboard from '@/pages/Dashboard'
import NewRecommendation from '@/pages/NewRecommendation'
import Result from '@/pages/Result'
import Fields from '@/pages/Fields'
import History from '@/pages/History'
import CropGuide from '@/pages/CropGuide'
import Profile from '@/pages/Profile'
import Login from '@/pages/Login'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const user = useAppStore((s) => s.user)
  const location = useLocation()
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<RequireAuth><Layout /></RequireAuth>}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/recommend" element={<NewRecommendation />} />
          <Route path="/result" element={<Result />} />
          <Route path="/fields" element={<Fields />} />
          <Route path="/history" element={<History />} />
          <Route path="/guide" element={<CropGuide />} />
          <Route path="/analytics" element={<Navigate to="/guide" replace />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

import { Navigate, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useAuth } from './hooks/useAuth'
import { LoginPage } from './pages/LoginPage'
import { SignupPage } from './pages/SignupPage'
import { VideoListPage } from './pages/VideoListPage'
import { VideoDetailPage } from './pages/VideoDetailPage'

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth()
  if (isLoading) return <p>Loading…</p>
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route
        path="/videos"
        element={
          <RequireAuth>
            <VideoListPage />
          </RequireAuth>
        }
      />
      <Route
        path="/videos/:videoId"
        element={
          <RequireAuth>
            <VideoDetailPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/videos" replace />} />
    </Routes>
  )
}

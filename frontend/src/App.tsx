import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import InspectionPage from './pages/InspectionPage'
import DashboardPage from './pages/DashboardPage'
import Layout from './components/Layout'

function App() {
  // Login deshabilitado - acceso directo
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <Layout>
              <Navigate to="/inspection" replace />
            </Layout>
          }
        />
        <Route
          path="/inspection"
          element={
            <Layout>
              <InspectionPage />
            </Layout>
          }
        />
        <Route
          path="/dashboard"
          element={
            <Layout>
              <DashboardPage />
            </Layout>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App

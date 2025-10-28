import { useState, useEffect } from 'react'
import { BarChart3, AlertTriangle, CheckCircle, HelpCircle } from 'lucide-react'
import api from '../services/api'
import type { CleaningEvent } from '../types'

export default function DashboardPage() {
  const [events, setEvents] = useState<CleaningEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    clean: 0,
    dirty: 0,
    uncertain: 0
  })

  useEffect(() => {
    fetchEvents()
  }, [])

  const fetchEvents = async () => {
    try {
      const response = await api.get<CleaningEvent[]>('/events?limit=50')
      setEvents(response.data)

      // Calculate stats
      const clean = response.data.filter(e => e.estado === 'clean').length
      const dirty = response.data.filter(e => e.estado === 'dirty').length
      const uncertain = response.data.filter(e => e.estado === 'uncertain').length

      setStats({
        total: response.data.length,
        clean,
        dirty,
        uncertain
      })
    } catch (error) {
      console.error('Error fetching events:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-CL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStateBadge = (state: string) => {
    switch (state) {
      case 'clean':
        return <span className="badge badge-success">Limpio</span>
      case 'dirty':
        return <span className="badge badge-danger">Sucio</span>
      case 'uncertain':
        return <span className="badge badge-warning">Dudoso</span>
      default:
        return <span className="badge badge-info">{state}</span>
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 animate-pulse mx-auto mb-2" />
          <p>Cargando dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
              <p className="text-3xl font-bold">{stats.total}</p>
            </div>
            <BarChart3 className="w-10 h-10 text-primary-500" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Limpios</p>
              <p className="text-3xl font-bold text-green-600">{stats.clean}</p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {stats.total > 0 ? Math.round((stats.clean / stats.total) * 100) : 0}%
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Sucios</p>
              <p className="text-3xl font-bold text-red-600">{stats.dirty}</p>
            </div>
            <AlertTriangle className="w-10 h-10 text-red-500" />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {stats.total > 0 ? Math.round((stats.dirty / stats.total) * 100) : 0}%
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Dudosos</p>
              <p className="text-3xl font-bold text-yellow-600">{stats.uncertain}</p>
            </div>
            <HelpCircle className="w-10 h-10 text-yellow-500" />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {stats.total > 0 ? Math.round((stats.uncertain / stats.total) * 100) : 0}%
          </p>
        </div>
      </div>

      {/* Recent events */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Inspecciones Recientes</h2>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b dark:border-gray-700">
                <th className="text-left py-3 px-2">PPU</th>
                <th className="text-left py-3 px-2">Operario</th>
                <th className="text-left py-3 px-2">Estado</th>
                <th className="text-left py-3 px-2">Confianza</th>
                <th className="text-left py-3 px-2">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {events.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-gray-500">
                    No hay inspecciones registradas
                  </td>
                </tr>
              ) : (
                events.map((event) => (
                  <tr key={event.id} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                    <td className="py-3 px-2 font-medium">{event.bus_ppu}</td>
                    <td className="py-3 px-2">{event.user_nombre}</td>
                    <td className="py-3 px-2">{getStateBadge(event.estado)}</td>
                    <td className="py-3 px-2">
                      {event.confidence ? `${(event.confidence * 100).toFixed(0)}%` : '-'}
                    </td>
                    <td className="py-3 px-2 text-sm text-gray-600">
                      {formatDate(event.created_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

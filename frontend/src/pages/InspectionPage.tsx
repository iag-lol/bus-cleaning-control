import { useState, useEffect, useRef } from 'react'
import { Camera, Upload, Send, Check, AlertCircle, HelpCircle } from 'lucide-react'
import api from '../services/api'
import type { Bus, CleaningState, AnalysisResponse } from '../types'

export default function InspectionPage() {
  const [buses, setBuses] = useState<Bus[]>([])
  const [selectedBusId, setSelectedBusId] = useState<number | null>(null)
  const [newPPU, setNewPPU] = useState('')
  const [showNewPPU, setShowNewPPU] = useState(false)

  const [cameraActive, setCameraActive] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)

  const [observations, setObservations] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const analysisIntervalRef = useRef<number | null>(null)

  // Fetch buses
  useEffect(() => {
    fetchBuses()
  }, [])

  const fetchBuses = async () => {
    try {
      const response = await api.get<Bus[]>('/buses')
      setBuses(response.data)
    } catch (error) {
      console.error('Error fetching buses:', error)
    }
  }

  const createNewBus = async () => {
    if (!newPPU.trim()) return

    try {
      const response = await api.post<Bus>('/buses', { ppu: newPPU.toUpperCase() })
      setBuses([...buses, response.data])
      setSelectedBusId(response.data.id)
      setNewPPU('')
      setShowNewPPU(false)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error al crear PPU')
    }
  }

  // Start camera
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: 1280, height: 720 }
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        setCameraActive(true)

        // Start automatic analysis
        startAutomaticAnalysis()
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      alert('No se pudo acceder a la cámara. Usa "Subir Foto" en su lugar.')
    }
  }

  // Stop camera
  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      stream.getTracks().forEach(track => track.stop())
      videoRef.current.srcObject = null
    }
    setCameraActive(false)
    stopAutomaticAnalysis()
  }

  // Automatic analysis
  const startAutomaticAnalysis = () => {
    const interval = setInterval(() => {
      if (!analyzing) {
        captureAndAnalyze()
      }
    }, 500) // Every 500ms

    analysisIntervalRef.current = interval as unknown as number
  }

  const stopAutomaticAnalysis = () => {
    if (analysisIntervalRef.current) {
      clearInterval(analysisIntervalRef.current)
      analysisIntervalRef.current = null
    }
  }

  // Capture frame and analyze
  const captureAndAnalyze = async () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.drawImage(video, 0, 0)

    // Convert to base64
    const base64 = canvas.toDataURL('image/jpeg', 0.8).split(',')[1]

    setAnalyzing(true)

    try {
      const response = await api.post<AnalysisResponse>('/ai/analyze', {
        image_base64: base64
      })

      setAnalysis(response.data)
    } catch (error) {
      console.error('Error analyzing image:', error)
    } finally {
      setAnalyzing(false)
    }
  }

  // Submit event
  const submitEvent = async () => {
    if (!selectedBusId || !analysis) {
      alert('Selecciona un bus y espera el análisis')
      return
    }

    setSubmitting(true)

    try {
      await api.post('/events', {
        bus_id: selectedBusId,
        estado: analysis.estado,
        confidence: analysis.confidence,
        observaciones: observations || null,
        origen: 'edge',
        issues: {
          issues: analysis.issues,
          suggestions: analysis.suggestions
        }
      })

      alert('Registro enviado exitosamente')
      setObservations('')
      setAnalysis(null)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error al enviar registro')
    } finally {
      setSubmitting(false)
    }
  }

  // Get badge style
  const getBadgeClass = (state: CleaningState) => {
    switch (state) {
      case 'clean': return 'badge badge-success'
      case 'dirty': return 'badge badge-danger'
      case 'uncertain': return 'badge badge-warning'
      default: return 'badge badge-info'
    }
  }

  const getStateIcon = (state: CleaningState) => {
    switch (state) {
      case 'clean': return <Check className="w-5 h-5" />
      case 'dirty': return <AlertCircle className="w-5 h-5" />
      case 'uncertain': return <HelpCircle className="w-5 h-5" />
    }
  }

  const getStateText = (state: CleaningState) => {
    switch (state) {
      case 'clean': return 'LIMPIO'
      case 'dirty': return 'SUCIO'
      case 'uncertain': return 'DUDOSO'
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">Inspección de Aseo</h1>

      {/* Bus selector */}
      <div className="card">
        <label className="block text-sm font-medium mb-2">
          Seleccionar PPU (Patente)
        </label>

        {!showNewPPU ? (
          <div className="flex gap-2">
            <select
              className="input flex-1"
              value={selectedBusId || ''}
              onChange={(e) => setSelectedBusId(Number(e.target.value) || null)}
            >
              <option value="">Seleccionar bus...</option>
              {buses.map(bus => (
                <option key={bus.id} value={bus.id}>
                  {bus.ppu} {bus.alias ? `(${bus.alias})` : ''}
                </option>
              ))}
            </select>
            <button
              className="btn btn-secondary"
              onClick={() => setShowNewPPU(true)}
            >
              Nuevo PPU
            </button>
          </div>
        ) : (
          <div className="flex gap-2">
            <input
              className="input flex-1"
              placeholder="Ej: ABCD12"
              value={newPPU}
              onChange={(e) => setNewPPU(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && createNewBus()}
            />
            <button className="btn btn-primary" onClick={createNewBus}>
              Crear
            </button>
            <button className="btn btn-secondary" onClick={() => setShowNewPPU(false)}>
              Cancelar
            </button>
          </div>
        )}
      </div>

      {/* Camera */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Cámara</h2>
          {cameraActive ? (
            <button className="btn btn-danger" onClick={stopCamera}>
              Detener Cámara
            </button>
          ) : (
            <button className="btn btn-primary" onClick={startCamera}>
              <Camera className="w-5 h-5 mr-2" />
              Activar Cámara
            </button>
          )}
        </div>

        <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />

          {/* Analysis overlay */}
          {analysis && cameraActive && (
            <div className="absolute top-4 left-4 right-4">
              <div className="flex items-center justify-between bg-black/70 rounded-lg p-3">
                <div className="flex items-center gap-3">
                  {getStateIcon(analysis.estado)}
                  <span className="text-white font-bold text-lg">
                    {getStateText(analysis.estado)}
                  </span>
                  <span className={getBadgeClass(analysis.estado)}>
                    {(analysis.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                {analyzing && (
                  <div className="text-white text-sm">Analizando...</div>
                )}
              </div>
            </div>
          )}
        </div>

        <canvas ref={canvasRef} className="hidden" />
      </div>

      {/* Analysis results */}
      {analysis && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-3">Resultado del Análisis</h3>

          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-medium">Estado:</span>
              <span className={getBadgeClass(analysis.estado)}>
                {getStateText(analysis.estado)}
              </span>
              <span className="text-sm text-gray-600">
                Confianza: {(analysis.confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {analysis.issues.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium mb-2">Problemas Detectados:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {analysis.issues.map((issue, i) => (
                  <li key={i} className="text-red-600 dark:text-red-400">{issue}</li>
                ))}
              </ul>
            </div>
          )}

          {analysis.suggestions.length > 0 && (
            <div>
              <h4 className="font-medium mb-2">Sugerencias:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {analysis.suggestions.map((suggestion, i) => (
                  <li key={i} className="text-primary-600 dark:text-primary-400">
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Observations */}
      <div className="card">
        <label className="block text-sm font-medium mb-2">
          Observaciones (Opcional)
        </label>
        <textarea
          className="input"
          rows={3}
          placeholder="Agregar notas adicionales..."
          value={observations}
          onChange={(e) => setObservations(e.target.value)}
        />
      </div>

      {/* Submit */}
      <button
        className="btn btn-primary w-full py-3 text-lg"
        onClick={submitEvent}
        disabled={!selectedBusId || !analysis || submitting}
      >
        <Send className="w-5 h-5 mr-2" />
        {submitting ? 'Enviando...' : 'Enviar Registro'}
      </button>
    </div>
  )
}

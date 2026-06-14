import { useState, useEffect } from 'react'

export interface Stats {
  total_leads: number
  leads_nuevos: number
  leads_interesados: number
  leads_en_seguimiento: number
  leads_convertidos: number
  leads_rechazados: number
  cotizaciones_generadas: number
  cotizaciones_aceptadas: number
  inversion_total: number
  tasa_conversion: number
}

export function useStats() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/stats/`)
      if (!res.ok) throw new Error('Error al obtener estadísticas')
      const data = await res.json()
      setStats(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Actualizar cada 5 segundos
    return () => clearInterval(interval)
  }, [])

  return { stats, loading, error, refetch: fetchStats }
}

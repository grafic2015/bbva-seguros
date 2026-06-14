import { useState } from 'react'

export interface Cotizacion {
  id: number
  lead_id: number
  marca: string
  modelo: string
  año: number
  prima_mensual: number
  prima_anual: number
  descuento_porcentaje: number
  estado: string
  fecha_generacion: string
}

export function useCotizaciones() {
  const [cotizaciones, setCotizaciones] = useState<Cotizacion[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const obtenerCotizacionesLead = async (leadId: number) => {
    setLoading(true)
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/cotizaciones/lead/${leadId}`)
      if (!res.ok) throw new Error('Error al obtener cotizaciones')
      const data = await res.json()
      setCotizaciones(Array.isArray(data) ? data : [])
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  const crearCotizacion = async (cotizacion: {
    lead_id: number
    marca: string
    modelo: string
    año: number
    prima_mensual: number
    descuento_porcentaje?: number
  }) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/cotizaciones/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...cotizacion,
          responsabilidad_civil: true,
          robo: true,
          colision: true,
          asistencia_24h: true,
          descuento_porcentaje: cotizacion.descuento_porcentaje || 35
        })
      })
      if (!res.ok) throw new Error('Error al crear cotización')
      const newCot = await res.json()
      setCotizaciones([newCot, ...cotizaciones])
      return newCot
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      throw err
    }
  }

  return {
    cotizaciones,
    loading,
    error,
    obtenerCotizacionesLead,
    crearCotizacion
  }
}

import { useState, useEffect } from 'react'

export interface Lead {
  id: number
  nombre: string
  usuario_instagram: string
  email?: string
  telefono?: string
  marca?: string
  modelo?: string
  año?: number
  localidad?: string
  estado: 'nuevo' | 'interesado' | 'en_seguimiento' | 'convertido' | 'rechazado'
  calificacion: 'alto' | 'medio' | 'bajo'
  cotizacion_generada: boolean
  monto_cotizado?: number
  fecha_creacion: string
  fecha_actualizacion: string
}

export function useLeads() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchLeads = async (filtro?: string) => {
    setLoading(true)
    try {
      const base = import.meta.env.VITE_API_URL || ''
      let url = `${base}/api/leads/`
      if (filtro && filtro !== 'todos') {
        url = `${base}/api/leads/estado/${filtro}`
      }
      const res = await fetch(url)
      if (!res.ok) throw new Error('Error al obtener leads')
      const data = await res.json()
      setLeads(Array.isArray(data) ? data : data.leads || [])
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  const crearLead = async (lead: {
    nombre: string
    usuario_instagram: string
    email?: string
    telefono?: string
    marca?: string
    modelo?: string
    año?: number
    localidad?: string
    comentario_inicial?: string
  }) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/leads/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(lead)
      })
      if (!res.ok) throw new Error('Error al crear lead')
      const newLead = await res.json()
      setLeads([newLead, ...leads])
      return newLead
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      throw err
    }
  }

  const actualizarEstado = async (leadId: number, nuevoEstado: string) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/leads/${leadId}/estado/${nuevoEstado}`, {
        method: 'PATCH'
      })
      if (!res.ok) throw new Error('Error al actualizar estado')
      const updated = await res.json()
      setLeads(leads.map(l => l.id === leadId ? updated : l))
      return updated
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      throw err
    }
  }

  const obtenerLeadPorId = async (leadId: number) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/leads/${leadId}`)
      if (!res.ok) throw new Error('Lead no encontrado')
      return await res.json()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      throw err
    }
  }

  useEffect(() => {
    fetchLeads()
  }, [])

  return {
    leads,
    loading,
    error,
    fetchLeads,
    crearLead,
    actualizarEstado,
    obtenerLeadPorId
  }
}

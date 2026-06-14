import { useState } from 'react'

export interface Conversacion {
  id: number
  lead_id: number
  mensaje_usuario: string
  mensaje_respuesta?: string
  tipo: string
  fecha: string
}

export function useConversaciones() {
  const [conversaciones, setConversaciones] = useState<Conversacion[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const obtenerConversacionesLead = async (leadId: number) => {
    setLoading(true)
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/conversaciones/lead/${leadId}`)
      if (!res.ok) throw new Error('Error al obtener conversaciones')
      const data = await res.json()
      setConversaciones(Array.isArray(data) ? data : [])
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  const crearConversacion = async (leadId: number, mensaje: string, respuesta?: string) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/conversaciones/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lead_id: leadId,
          mensaje_usuario: mensaje,
          mensaje_respuesta: respuesta,
          tipo: 'chat'
        })
      })
      if (!res.ok) throw new Error('Error al crear conversación')
      const newConv = await res.json()
      setConversaciones([newConv, ...conversaciones])
      return newConv
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      throw err
    }
  }

  return {
    conversaciones,
    loading,
    error,
    obtenerConversacionesLead,
    crearConversacion
  }
}

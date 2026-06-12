import { useEffect, useState, useRef } from 'react'
import { useConversaciones } from '../hooks/useConversaciones'
import type { Lead } from '../hooks/useLeads'

interface ConversacionPanelProps {
  lead: Lead | null
}

export function ConversacionPanel({ lead }: ConversacionPanelProps) {
  const { conversaciones, obtenerConversacionesLead, crearConversacion } = useConversaciones()
  const [mensaje, setMensaje] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (lead) {
      obtenerConversacionesLead(lead.id)
    }
  }, [lead])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [conversaciones])

  if (!lead) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
        Selecciona un lead para ver conversaciones
      </div>
    )
  }

  const handleEnviar = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!mensaje.trim()) return

    setLoading(true)
    try {
      const respuesta = `Gracias por tu interés ${lead.nombre}. Estamos procesando tu cotización. Te contactaremos en breve.`
      await crearConversacion(lead.id, mensaje, respuesta)
      setMensaje('')
    } catch (err) {
      alert('❌ Error: ' + (err instanceof Error ? err.message : 'Desconocido'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#161b22', borderRadius: '8px' }}>
      <div style={{ padding: '15px', borderBottom: '1px solid #30363d' }}>
        <h3 style={{ margin: '0', fontSize: '24px' }}>💬 Conversaciones</h3>
        <p style={{ margin: '5px 0 0 0', fontSize: '16px', color: '#888' }}>
          {conversaciones.length} mensajes
        </p>
      </div>

      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '15px',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px'
        }}
      >
        {conversaciones.length === 0 ? (
          <div style={{ color: '#888', textAlign: 'center', marginTop: '20px' }}>
            Sin conversaciones aún
          </div>
        ) : (
          conversaciones.map(conv => (
            <div key={conv.id} style={{ display: 'grid', gap: '8px' }}>
              <div
                style={{
                  padding: '10px',
                  background: '#0d1117',
                  borderRadius: '6px',
                  borderLeft: '3px solid #667eea',
                  alignSelf: 'flex-end',
                  maxWidth: '85%'
                }}
              >
                <p style={{ margin: '0', fontSize: '18px', wordBreak: 'break-word' }}>
                  {conv.mensaje_usuario}
                </p>
                <small style={{ color: '#888', marginTop: '5px' }}>
                  {new Date(conv.fecha).toLocaleTimeString()}
                </small>
              </div>

              {conv.mensaje_respuesta && (
                <div
                  style={{
                    padding: '10px',
                    background: '#0d1117',
                    borderRadius: '6px',
                    borderLeft: '3px solid #00cc00',
                    alignSelf: 'flex-start',
                    maxWidth: '85%'
                  }}
                >
                  <p style={{ margin: '0', fontSize: '18px', color: '#87CEEB', wordBreak: 'break-word' }}>
                    {conv.mensaje_respuesta}
                  </p>
                  <small style={{ color: '#888', marginTop: '5px' }}>
                    Bot BBVA
                  </small>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <form
        onSubmit={handleEnviar}
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr auto',
          gap: '10px',
          padding: '15px',
          borderTop: '1px solid #30363d'
        }}
      >
        <input
          type="text"
          value={mensaje}
          onChange={e => setMensaje(e.target.value)}
          placeholder="Escribe un mensaje..."
          disabled={loading}
          style={{
            padding: '14px',
            borderRadius: '4px',
            border: '1px solid #30363d',
            background: '#0d1117',
            color: 'white',
            fontFamily: 'inherit',
            fontSize: '18px'
          }}
        />
        <button
          type="submit"
          disabled={loading || !mensaje.trim()}
          style={{
            padding: '14px 24px',
            background: loading || !mensaje.trim() ? '#555' : '#00cc00',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading || !mensaje.trim() ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
            fontSize: '18px'
          }}
        >
          {loading ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  )
}

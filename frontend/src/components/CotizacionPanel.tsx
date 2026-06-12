import { useEffect, useState } from 'react'
import { useCotizaciones } from '../hooks/useCotizaciones'
import type { Lead } from '../hooks/useLeads'

interface CotizacionPanelProps {
  lead: Lead | null
}

export function CotizacionPanel({ lead }: CotizacionPanelProps) {
  const { cotizaciones, obtenerCotizacionesLead, crearCotizacion } = useCotizaciones()
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (lead) {
      obtenerCotizacionesLead(lead.id)
    }
  }, [lead])

  if (!lead) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
        Selecciona un lead para ver cotizaciones
      </div>
    )
  }

  const handleCrearCotizacion = async () => {
    if (!lead.marca || !lead.modelo || !lead.año) {
      alert('❌ El lead debe tener marca, modelo y año para crear cotización')
      return
    }

    setLoading(true)
    try {
      // Calcular prima estimada
      const precioBase = 250 // Precio base mensual
      await crearCotizacion({
        lead_id: lead.id,
        marca: lead.marca,
        modelo: lead.modelo,
        año: lead.año,
        prima_mensual: precioBase,
        descuento_porcentaje: 35
      })
      setShowForm(false)
      alert('✅ Cotización creada correctamente')
    } catch (err) {
      alert('❌ Error: ' + (err instanceof Error ? err.message : 'Desconocido'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', borderRadius: '8px', background: '#161b22' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h3 style={{ margin: '0', fontSize: '24px' }}>💰 Cotizaciones ({cotizaciones.length})</h3>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            style={{
              padding: '12px 16px',
              background: '#00cc00',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '16px'
            }}
          >
            + Nueva
          </button>
        )}
      </div>

      {showForm && (
        <div
          style={{
            padding: '15px',
            background: '#0d1117',
            borderRadius: '6px',
            marginBottom: '15px',
            border: '1px solid #30363d'
          }}
        >
          <p style={{ margin: '0 0 10px 0', fontSize: '18px', color: '#888' }}>
            📋 {lead.marca} {lead.modelo} {lead.año}
          </p>
          <div style={{ display: 'grid', gap: '10px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '16px', color: '#888' }}>Prima Mensual</label>
                <p style={{ margin: '5px 0 0 0', fontSize: '18px', fontWeight: 'bold', color: '#00cc00' }}>
                  $250
                </p>
              </div>
              <div>
                <label style={{ fontSize: '16px', color: '#888' }}>Prima Anual</label>
                <p style={{ margin: '5px 0 0 0', fontSize: '18px', fontWeight: 'bold', color: '#00cc00' }}>
                  $3,000
                </p>
              </div>
              <div>
                <label style={{ fontSize: '16px', color: '#888' }}>Descuento</label>
                <p style={{ margin: '5px 0 0 0', fontSize: '18px', fontWeight: 'bold', color: '#FFD700' }}>
                  35%
                </p>
              </div>
              <div>
                <label style={{ fontSize: '16px', color: '#888' }}>A pagar</label>
                <p style={{ margin: '5px 0 0 0', fontSize: '18px', fontWeight: 'bold', color: '#87CEEB' }}>
                  $162.50
                </p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '10px' }}>
              <button
                onClick={() => setShowForm(false)}
                style={{
                  padding: '10px',
                  background: '#555',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Cancelar
              </button>
              <button
                onClick={handleCrearCotizacion}
                disabled={loading}
                style={{
                  padding: '10px',
                  background: loading ? '#444' : '#00cc00',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold'
                }}
              >
                {loading ? '⏳ Generando...' : '✓ Generar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {cotizaciones.length === 0 ? (
        <p style={{ color: '#888', margin: '0', fontSize: '14px' }}>Sin cotizaciones aún</p>
      ) : (
        <div style={{ display: 'grid', gap: '10px' }}>
          {cotizaciones.map(cot => (
            <div
              key={cot.id}
              style={{
                padding: '12px',
                background: '#0d1117',
                borderRadius: '6px',
                border: '1px solid #30363d'
              }}
            >
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ fontSize: '16px', color: '#888' }}>Prima</label>
                  <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#00cc00' }}>
                    ${cot.prima_mensual.toFixed(2)}/mes
                  </p>
                </div>
                <div>
                  <label style={{ fontSize: '16px', color: '#888' }}>Descuento</label>
                  <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#FFD700' }}>
                    {cot.descuento_porcentaje}%
                  </p>
                </div>
                <div>
                  <label style={{ fontSize: '16px', color: '#888' }}>Estado</label>
                  <p style={{
                    margin: '5px 0 0 0',
                    fontWeight: 'bold',
                    color: cot.estado === 'aceptada' ? '#00cc00' : '#FFD700'
                  }}>
                    {cot.estado}
                  </p>
                </div>
              </div>
              <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: '#888' }}>
                {new Date(cot.fecha_generacion).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

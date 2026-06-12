import { useState } from 'react'
import { useLeads, type Lead } from '../hooks/useLeads'
import './LeadsTable.css'

export function LeadsTableNew() {
  const { leads, loading, fetchLeads, actualizarEstado } = useLeads()
  const [filtro, setFiltro] = useState('todos')
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)

  const handleFiltro = (f: string) => {
    setFiltro(f)
    fetchLeads(f === 'todos' ? undefined : f)
  }

  const handleEstado = async (leadId: number, nuevoEstado: string) => {
    await actualizarEstado(leadId, nuevoEstado)
  }

  const getColorEstado = (estado: string) => {
    const colores: Record<string, string> = {
      nuevo: '#FFD700',
      interesado: '#87CEEB',
      en_seguimiento: '#FFA500',
      convertido: '#00CC00',
      rechazado: '#FF6B6B'
    }
    return colores[estado] || '#888'
  }

  const getColorCalificacion = (calificacion: string) => {
    const colores: Record<string, string> = {
      alto: '#00CC00',
      medio: '#FFD700',
      bajo: '#FF6B6B'
    }
    return colores[calificacion] || '#888'
  }

  return (
    <div className="leads-table-container">
      <div className="leads-header">
        <h2>📋 Leads ({leads.length})</h2>
        <div className="filtros">
          {['todos', 'nuevo', 'interesado', 'en_seguimiento', 'convertido', 'rechazado'].map(f => (
            <button
              key={f}
              className={`filtro-btn ${filtro === f ? 'active' : ''}`}
              onClick={() => handleFiltro(f)}
            >
              {f === 'todos' ? 'Todos' : f.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {loading && <div className="loading">Cargando leads...</div>}

      <div className="table-wrapper">
        <table className="leads-table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Nombre</th>
              <th>Vehículo</th>
              <th>Localidad</th>
              <th>Estado</th>
              <th>Calificación</th>
              <th>Cotización</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {leads.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', color: '#888', padding: '20px' }}>
                  Sin leads aún
                </td>
              </tr>
            ) : (
              leads.map(lead => (
                <tr key={lead.id} style={{ borderLeft: `4px solid ${getColorEstado(lead.estado)}` }}>
                  <td className="usuario">@{lead.usuario_instagram}</td>
                  <td>{lead.nombre}</td>
                  <td>
                    {lead.marca && lead.modelo ? `${lead.marca} ${lead.modelo} ${lead.año || ''}` : '—'}
                  </td>
                  <td>{lead.localidad || '—'}</td>
                  <td>
                    <span
                      style={{
                        color: getColorEstado(lead.estado),
                        fontWeight: 'bold',
                        cursor: 'pointer'
                      }}
                      onClick={() => {
                        const estados = ['nuevo', 'interesado', 'en_seguimiento', 'convertido', 'rechazado']
                        const idx = estados.indexOf(lead.estado)
                        const siguiente = estados[(idx + 1) % estados.length]
                        handleEstado(lead.id, siguiente)
                      }}
                      title="Click para avanzar estado"
                    >
                      {lead.estado}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: getColorCalificacion(lead.calificacion), fontWeight: 'bold' }}>
                      {lead.calificacion}
                    </span>
                  </td>
                  <td>
                    {lead.cotizacion_generada ? (
                      <span style={{ color: '#00CC00', fontWeight: 'bold' }}>
                        ✓ ${lead.monto_cotizado?.toFixed(2)}
                      </span>
                    ) : (
                      <span style={{ color: '#888' }}>—</span>
                    )}
                  </td>
                  <td>
                    <button
                      className="btn-detalle"
                      onClick={() => setSelectedLead(lead)}
                      title="Ver detalles"
                    >
                      👁
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal de detalles */}
      {selectedLead && (
        <div className="modal-overlay" onClick={() => setSelectedLead(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📝 Detalle de Lead</h3>
              <button onClick={() => setSelectedLead(null)} className="close-btn">✕</button>
            </div>

            <div className="modal-body">
              <div className="info-grid">
                <div className="info-item">
                  <label>Usuario Instagram</label>
                  <p>@{selectedLead.usuario_instagram}</p>
                </div>
                <div className="info-item">
                  <label>Nombre</label>
                  <p>{selectedLead.nombre}</p>
                </div>
                <div className="info-item">
                  <label>Email</label>
                  <p>{selectedLead.email || '—'}</p>
                </div>
                <div className="info-item">
                  <label>Teléfono</label>
                  <p>{selectedLead.telefono || '—'}</p>
                </div>
                <div className="info-item">
                  <label>Marca</label>
                  <p>{selectedLead.marca || '—'}</p>
                </div>
                <div className="info-item">
                  <label>Modelo</label>
                  <p>{selectedLead.modelo || '—'}</p>
                </div>
                <div className="info-item">
                  <label>Año</label>
                  <p>{selectedLead.año || '—'}</p>
                </div>
                <div className="info-item">
                  <label>Localidad</label>
                  <p>{selectedLead.localidad || '—'}</p>
                </div>
                <div className="info-item">
                  <label>Estado</label>
                  <p style={{ color: getColorEstado(selectedLead.estado), fontWeight: 'bold' }}>
                    {selectedLead.estado}
                  </p>
                </div>
                <div className="info-item">
                  <label>Calificación</label>
                  <p style={{ color: getColorCalificacion(selectedLead.calificacion), fontWeight: 'bold' }}>
                    {selectedLead.calificacion}
                  </p>
                </div>
                <div className="info-item">
                  <label>Cotización</label>
                  <p>
                    {selectedLead.cotizacion_generada ? `$${selectedLead.monto_cotizado?.toFixed(2)}` : '—'}
                  </p>
                </div>
                <div className="info-item">
                  <label>Creado</label>
                  <p>{new Date(selectedLead.fecha_creacion).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

import { useState } from 'react'
import Scene3D from './components/Scene3D'
import { LeadsTableNew } from './components/LeadsTableNew'
import { LeadsForm } from './components/LeadsForm'
import { CotizacionPanel } from './components/CotizacionPanel'
import { ConversacionPanel } from './components/ConversacionPanel'
import { StatsPanel } from './components/StatsPanel'
import { useLeads, type Lead } from './hooks/useLeads'

export default function AppSeguros() {
  const { leads } = useLeads()
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [activeTab, setActiveTab] = useState<'tabla' | 'detalle'>('tabla')

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0d1117', color: 'white', fontFamily: 'Arial, sans-serif' }}>
      {/* Panel izquierdo - Tabla y Formulario */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', borderRight: '1px solid #30363d', overflow: 'hidden' }}>
        <div style={{ padding: '30px', borderBottom: '1px solid #30363d', background: '#161b22' }}>
          <h1 style={{ margin: '0', fontSize: '32px' }}>🚗 BBVA Seguros Auto</h1>
          <p style={{ margin: '5px 0 0 0', fontSize: '18px', color: '#888' }}>Sistema de Gestión de Leads</p>
        </div>

        <div style={{ padding: '20px', overflow: 'auto', flex: 1 }}>
          <LeadsForm />
          <div style={{ marginTop: '20px' }}>
            <LeadsTableNew />
          </div>
        </div>
      </div>

      {/* Panel central - Escena 3D */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', borderRight: '1px solid #30363d', overflow: 'hidden' }}>
        <div style={{ padding: '25px', borderBottom: '1px solid #30363d', background: '#161b22' }}>
          <h2 style={{ margin: '0', fontSize: '24px' }}>🎮 Escena 3D</h2>
          <p style={{ margin: '5px 0 0 0', fontSize: '16px', color: '#888' }}>
            ⬆️⬇️⬅️➡️ Mover auto · 🖱️ Rotar cámara
          </p>
        </div>
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <Scene3D />
        </div>
      </div>

      {/* Panel derecho - Detalles y Cotizaciones */}
      <div style={{ width: '400px', display: 'flex', flexDirection: 'column', borderLeft: '1px solid #30363d', overflow: 'hidden' }}>
        <div style={{ padding: '30px', borderBottom: '1px solid #30363d', background: '#161b22' }}>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
            <button
              onClick={() => setActiveTab('tabla')}
              style={{
                flex: 1,
                padding: '8px',
                background: activeTab === 'tabla' ? '#667EEA' : '#30363d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '18px',
                fontWeight: 'bold'
              }}
            >
              Estadísticas
            </button>
            <button
              onClick={() => setActiveTab('detalle')}
              style={{
                flex: 1,
                padding: '8px',
                background: activeTab === 'detalle' ? '#667EEA' : '#30363d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '18px',
                fontWeight: 'bold'
              }}
            >
              Lead
            </button>
          </div>

          {activeTab === 'detalle' && selectedLead && (
            <div style={{ fontSize: '18px' }}>
              <p style={{ margin: '0 0 5px 0', fontWeight: 'bold', color: '#667EEA' }}>
                @{selectedLead.usuario_instagram}
              </p>
              <p style={{ margin: '0', color: '#888', fontSize: '16px' }}>
                {selectedLead.nombre}
              </p>
            </div>
          )}
        </div>

        <div style={{ flex: 1, overflow: 'auto', padding: '20px' }}>
          {activeTab === 'tabla' ? (
            <StatsPanel />
          ) : (
            <div style={{ display: 'grid', gridTemplateRows: '1fr 1fr', gap: '20px', height: '100%' }}>
              <CotizacionPanel lead={selectedLead} />
              <ConversacionPanel lead={selectedLead} />
            </div>
          )}
        </div>
      </div>

      {/* Modal para seleccionar lead - sobrescribe el que está en LeadsTableNew */}
      <script>
        {`
          // Intercept clicks en tabla para actualizar selectedLead
          document.addEventListener('click', (e) => {
            const leadRow = (e.target as HTMLElement).closest('tr[data-lead-id]');
            if (leadRow) {
              const leadId = leadRow.getAttribute('data-lead-id');
              window.dispatchEvent(new CustomEvent('selectLead', { detail: { id: leadId } }));
            }
          });
        `}
      </script>
    </div>
  )
}

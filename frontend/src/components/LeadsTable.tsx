import './LeadsTable.css'

interface Lead {
  id: string
  nombre: string
  usuario: string
  estado: string
  fecha: string
  comentario: string
  respuesta: string
}

interface LeadsTableProps {
  leads: Lead[]
}

const LeadsTable = ({ leads }: LeadsTableProps) => {
  return (
    <div className="leads-table">
      <div className="table-header">
        <div>👤 Usuario</div>
        <div>💬 Comentario</div>
        <div>📊 Estado</div>
        <div>📅 Fecha</div>
      </div>
      <div className="table-rows">
        {leads && leads.length > 0 ? (
          leads.map((lead) => (
            <div key={lead.id} className="table-row">
              <div>@{lead.usuario}</div>
              <div>{(lead.comentario || '').substring(0, 40)}...</div>
              <div>
                <span className="status-badge-table">{lead.estado}</span>
              </div>
              <div>{new Date(lead.fecha).toLocaleDateString('es-ES')}</div>
            </div>
          ))
        ) : (
          <div style={{
            padding: '20px',
            textAlign: 'center',
            color: '#a0aec0',
            gridColumn: '1 / -1'
          }}>
            Sin leads aún
          </div>
        )}
      </div>
    </div>
  )
}

export default LeadsTable

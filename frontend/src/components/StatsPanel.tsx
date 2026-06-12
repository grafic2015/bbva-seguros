import { useStats } from '../hooks/useStats'

export function StatsPanel() {
  const { stats, loading } = useStats()

  if (loading || !stats) {
    return <div style={{ padding: '20px', color: '#888' }}>Cargando estadísticas...</div>
  }

  const StatItem = ({ label, value, color }: { label: string; value: number | string; color: string }) => (
    <div style={{ textAlign: 'center', padding: '20px', background: '#0d1117', borderRadius: '6px' }}>
      <p style={{ margin: '0', fontSize: '18px', color: '#888' }}>{label}</p>
      <p style={{ margin: '12px 0 0 0', fontSize: '48px', fontWeight: 'bold', color }}>
        {typeof value === 'number' && label.includes('%') ? value.toFixed(1) : value}
      </p>
    </div>
  )

  return (
    <div style={{ padding: '20px', background: '#161b22', borderRadius: '8px' }}>
      <h3 style={{ margin: '0 0 15px 0' }}>📊 Estadísticas</h3>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
        <StatItem label="Total Leads" value={stats.total_leads} color="#667EEA" />
        <StatItem label="Nuevos" value={stats.leads_nuevos} color="#FFD700" />
        <StatItem label="Interesados" value={stats.leads_interesados} color="#87CEEB" />
        <StatItem label="En Seguimiento" value={stats.leads_en_seguimiento} color="#FFA500" />
        <StatItem label="Convertidos" value={stats.leads_convertidos} color="#00CC00" />
        <StatItem label="Rechazados" value={stats.leads_rechazados} color="#FF6B6B" />
      </div>

      <div style={{ borderTop: '1px solid #30363d', paddingTop: '20px', marginBottom: '20px' }}>
        <h4 style={{ margin: '0 0 15px 0', fontSize: '14px' }}>💰 Cotizaciones</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <StatItem label="Generadas" value={stats.cotizaciones_generadas} color="#667EEA" />
          <StatItem label="Aceptadas" value={stats.cotizaciones_aceptadas} color="#00CC00" />
          <StatItem label="Inversión Total" value={`$${stats.inversion_total.toFixed(0)}`} color="#87CEEB" />
          <StatItem label="Tasa Conversión" value={`${stats.tasa_conversion}%`} color="#FFD700" />
        </div>
      </div>

      <div style={{ borderTop: '1px solid #30363d', paddingTop: '20px' }}>
        <div style={{
          padding: '15px',
          background: '#0d1117',
          borderRadius: '6px',
          border: '1px solid #30363d'
        }}>
          <p style={{ margin: '0', fontSize: '12px', color: '#888' }}>
            🎯 Próxima Meta: 50 leads convertidos
          </p>
          <div style={{
            marginTop: '10px',
            width: '100%',
            height: '8px',
            background: '#30363d',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${(stats.leads_convertidos / 50) * 100}%`,
              background: stats.leads_convertidos >= 50 ? '#00CC00' : '#667EEA',
              transition: 'width 0.3s ease'
            }} />
          </div>
          <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: '#888' }}>
            {stats.leads_convertidos} / 50 ({((stats.leads_convertidos / 50) * 100).toFixed(1)}%)
          </p>
        </div>
      </div>
    </div>
  )
}

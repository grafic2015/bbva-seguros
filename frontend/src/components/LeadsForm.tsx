import { useState } from 'react'
import { useLeads } from '../hooks/useLeads'

export function LeadsForm() {
  const { crearLead } = useLeads()
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    nombre: '',
    usuario_instagram: '',
    email: '',
    telefono: '',
    marca: '',
    modelo: '',
    año: '',
    localidad: '',
    comentario_inicial: ''
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'año' && value ? parseInt(value) : value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await crearLead({
        ...formData,
        año: formData.año ? parseInt(formData.año) : undefined
      })
      setFormData({
        nombre: '',
        usuario_instagram: '',
        email: '',
        telefono: '',
        marca: '',
        modelo: '',
        año: '',
        localidad: '',
        comentario_inicial: ''
      })
      setShowForm(false)
      alert('✅ Lead creado correctamente')
    } catch (err) {
      alert('❌ Error al crear lead: ' + (err instanceof Error ? err.message : 'Desconocido'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', borderRadius: '8px', background: '#161b22' }}>
      <button
        onClick={() => setShowForm(!showForm)}
        style={{
          width: '100%',
          padding: '16px',
          background: showForm ? '#ff6b6b' : '#00cc00',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontWeight: 'bold',
          marginBottom: '15px',
          fontSize: '18px'
        }}
      >
        {showForm ? '✕ Cerrar' : '+ Nuevo Lead'}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '12px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <input
              type="text"
              name="nombre"
              placeholder="Nombre *"
              value={formData.nombre}
              onChange={handleChange}
              required
              style={{ padding: '12px', borderRadius: '4px', border: '1px solid #30363d', background: '#0d1117', color: 'white', fontSize: '16px' }}
            />
            <input
              type="text"
              name="usuario_instagram"
              placeholder="Usuario Instagram *"
              value={formData.usuario_instagram}
              onChange={handleChange}
              required
              style={{ padding: '12px', borderRadius: '4px', border: '1px solid #30363d', background: '#0d1117', color: 'white', fontSize: '16px' }}
            />
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              style={{ padding: '12px', borderRadius: '4px', border: '1px solid #30363d', background: '#0d1117', color: 'white', fontSize: '16px' }}
            />
            <input
              type="tel"
              name="telefono"
              placeholder="Teléfono"
              value={formData.telefono}
              onChange={handleChange}
              style={{ padding: '12px', borderRadius: '4px', border: '1px solid #30363d', background: '#0d1117', color: 'white', fontSize: '16px' }}
            />
            <input
              type="text"
              name="marca"
              placeholder="Marca del auto"
              value={formData.marca}
              onChange={handleChange}
              style={{ padding: '12px', borderRadius: '4px', border: '1px solid #30363d', background: '#0d1117', color: 'white', fontSize: '16px' }}
            />
            <input
              type="text"
              name="modelo"
              placeholder="Modelo del auto"
              value={formData.modelo}
              onChange={handleChange}
              style={{ padding: '12px', borderRadius: '4px', border: '1px solid #30363d', background: '#0d1117', color: 'white', fontSize: '16px' }}
            />
            <input
              type="number"
              name="año"
              placeholder="Año"
              value={formData.año}
              onChange={handleChange}
              min="1990"
              max={new Date().getFullYear()}
              style={{ padding: '12px', borderRadius: '4px', border: '1px solid #30363d', background: '#0d1117', color: 'white', fontSize: '16px' }}
            />
            <input
              type="text"
              name="localidad"
              placeholder="Localidad"
              value={formData.localidad}
              onChange={handleChange}
              style={{ padding: '12px', borderRadius: '4px', border: '1px solid #30363d', background: '#0d1117', color: 'white', fontSize: '16px' }}
            />
          </div>

          <textarea
            name="comentario_inicial"
            placeholder="Comentario inicial (opcional)"
            value={formData.comentario_inicial}
            onChange={handleChange}
            style={{
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #30363d',
              background: '#0d1117',
              color: 'white',
              minHeight: '80px',
              fontFamily: 'inherit'
            }}
          />

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '14px',
              background: loading ? '#555' : '#00cc00',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
              fontSize: '16px'
            }}
          >
            {loading ? '⏳ Guardando...' : '✓ Crear Lead'}
          </button>
        </form>
      )}
    </div>
  )
}

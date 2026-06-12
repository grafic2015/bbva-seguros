import { useState } from 'react'
import './Sidebar.css'

interface EstadoAgente {
  status: string
  mensaje: string
  leads_encontrados: number
  dms_enviados: number
  progreso: number
  total_leads?: number
}

interface SidebarProps {
  estado: {
    monitor: EstadoAgente
    manager: EstadoAgente
  }
  onRunAgent: (agent: string) => void
  messages: any[]
  onSendMessage: (message: string) => void
}

const Sidebar = ({ estado, onRunAgent, messages, onSendMessage }: SidebarProps) => {
  const [chatInput, setChatInput] = useState('')

  const handleSend = () => {
    if (chatInput.trim()) {
      onSendMessage(chatInput)
      setChatInput('')
    }
  }

  return (
    <div className="sidebar">
      <div className="sidebar-header">🚗 Dashboard Autos 3D</div>

      <div className="agents-panel">
        <AgentCard
          name="Monitor"
          icon="📱"
          agente="monitor"
          estado={estado.monitor}
          onRun={() => onRunAgent('monitor')}
        />
        <AgentCard
          name="Manager"
          icon="📊"
          agente="manager"
          estado={estado.manager}
          onRun={() => onRunAgent('manager')}
        />
      </div>

      <div className="chat-panel">
        <div className="chat-title">💬 Chat</div>
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.tipo || 'info'}`}>
              <span className="chat-time">
                {new Date(msg.timestamp).toLocaleTimeString('es-ES', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
              <span className="chat-agent">{msg.agente}:</span>
              <span>{msg.mensaje.substring(0, 50)}</span>
            </div>
          ))}
        </div>
        <div className="chat-input-group">
          <input
            type="text"
            className="chat-input"
            placeholder="Escribe..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          />
          <button className="chat-send" onClick={handleSend}>
            📤
          </button>
        </div>
      </div>
    </div>
  )
}

interface AgentCardProps {
  name: string
  icon: string
  agente: string
  estado: EstadoAgente
  onRun: () => void
}

const AgentCard = ({ name, icon, agente, estado, onRun }: AgentCardProps) => {
  const getStatusClass = (status: string) => {
    switch (status) {
      case 'running': return 'status-running'
      case 'done': return 'status-done'
      case 'error': return 'status-error'
      default: return 'status-idle'
    }
  }

  return (
    <div className="agent-card">
      <div className="agent-name">
        {icon} {name}
        <span className={`status-badge ${getStatusClass(estado.status)}`}>
          {estado.status}
        </span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${estado.progreso}%` }}></div>
      </div>
      <div className="agent-msg">{estado.mensaje}</div>
      <button
        className="agent-button"
        onClick={onRun}
        disabled={estado.status === 'running'}
      >
        ▶ Ejecutar
      </button>
    </div>
  )
}

export default Sidebar

import { useState, useEffect } from "react";
import "../styles/settings.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Settings {
  JOB_KEYWORDS: string;
  JOB_LOCATION: string;
  JOB_MAX_RESULTS: number;
  JOB_SOLO_HOY: boolean;
  EMAIL_ADDRESS: string;
  EMAIL_PASSWORD: string;
  CV_FILE_PATH: string;
  EMAIL_SUBJECT: string;
  EMAIL_BODY: string;
  GEMINI_API_KEY: string;
  PUBLIC_URL: string;
  SCHEDULER_ENABLED: boolean;
  SCHEDULER_TIME: string;
  TELEGRAM_TOKEN: string;
  TELEGRAM_CHAT_ID: string;
  IMAP_AUTO_ENABLED: boolean;
  IMAP_INTERVAL_MINUTES: number;
  EXCLUDE_KEYWORDS: string;
  BLACKLIST_COMPANIES: string;
  JOB_MODALITY: string;
  EMAIL_BATCH_SIZE: number;
  EMAIL_BATCH_PAUSE: number;
  EMAIL_BUSINESS_HOURS: boolean;
  EMAIL_BH_START: number;
  EMAIL_BH_END: number;
  DRY_RUN: boolean;
}

const DEFAULTS: Settings = {
  JOB_KEYWORDS: "desarrollador Python",
  JOB_LOCATION: "Buenos Aires, Argentina",
  JOB_MAX_RESULTS: 30,
  JOB_SOLO_HOY: false,
  EMAIL_ADDRESS: "",
  EMAIL_PASSWORD: "",
  CV_FILE_PATH: "cv.pdf",
  EMAIL_SUBJECT: "Envío de CV - Emilio Pujalka – {job_title}",
  EMAIL_BODY: `Estimado equipo de {company_name}:\n\nMe pongo en contacto con ustedes para expresar mi interés en la posición de {job_title}.\n\nAdjunto mi currículum vitae para su consideración.\n\nSaludos cordiales,\nEmilio Pujalka`,
  GEMINI_API_KEY: "",
  PUBLIC_URL: "",
  SCHEDULER_ENABLED: false,
  SCHEDULER_TIME: "09:00",
  TELEGRAM_TOKEN: "",
  TELEGRAM_CHAT_ID: "",
  IMAP_AUTO_ENABLED: false,
  IMAP_INTERVAL_MINUTES: 30,
  EXCLUDE_KEYWORDS: "",
  BLACKLIST_COMPANIES: "",
  JOB_MODALITY: "",
  EMAIL_BATCH_SIZE: 10,
  EMAIL_BATCH_PAUSE: 300,
  EMAIL_BUSINESS_HOURS: false,
  EMAIL_BH_START: 9,
  EMAIL_BH_END: 18,
  DRY_RUN: false,
};

interface Props {
  onClose: () => void;
}

export default function SettingsPanel({ onClose }: Props) {
  const [form, setForm]     = useState<Settings>(DEFAULTS);
  const [saved, setSaved]   = useState(false);
  const [loading, setLoading] = useState(true);
  const [tab, setTab]       = useState<"search" | "email" | "filters" | "advanced">("search");

  useEffect(() => {
    fetch(`${API}/api/settings`)
      .then((r) => r.json())
      .then((data) => {
        setForm({ 
          ...DEFAULTS, 
          ...data,
          EXCLUDE_KEYWORDS: Array.isArray(data.EXCLUDE_KEYWORDS) ? data.EXCLUDE_KEYWORDS.join('\n') : (data.EXCLUDE_KEYWORDS || ''),
          BLACKLIST_COMPANIES: Array.isArray(data.BLACKLIST_COMPANIES) ? data.BLACKLIST_COMPANIES.join('\n') : (data.BLACKLIST_COMPANIES || ''),
        });
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    const payload = {
      ...form,
      EXCLUDE_KEYWORDS: form.EXCLUDE_KEYWORDS.split('\n').map(s => s.trim()).filter(Boolean),
      BLACKLIST_COMPANIES: form.BLACKLIST_COMPANIES.split('\n').map(s => s.trim()).filter(Boolean),
    };
    await fetch(`${API}/api/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const set = (key: keyof Settings, value: unknown) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  if (loading) {
    return (
      <div className="settings-overlay">
        <div className="settings-modal">
          <div className="settings-loading">Cargando configuración…</div>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="settings-modal">
        {/* Header */}
        <div className="settings-header">
          <div className="settings-title">
            <span className="settings-icon">⚙️</span>
            Configuración
          </div>
          <button className="settings-close" onClick={onClose}>✕</button>
        </div>

        {/* Tabs */}
        <div className="settings-tabs">
          {(["search", "filters", "email", "advanced"] as const).map((t) => (
            <button
              key={t}
              className={`settings-tab ${tab === t ? "active" : ""}`}
              onClick={() => setTab(t)}
            >
              {t === "search" ? "🔍 Búsqueda" : t === "filters" ? "🚫 Filtros" : t === "email" ? "📧 Correo" : "🔧 Avanzado"}
            </button>
          ))}
        </div>

        {/* Body */}
        <div className="settings-body">
          {tab === "search" && (
            <>
              <label className="settings-label">
                Palabras clave
                <input
                  className="settings-input"
                  value={form.JOB_KEYWORDS}
                  onChange={(e) => set("JOB_KEYWORDS", e.target.value)}
                  placeholder="Ej: desarrollador Python, soporte técnico"
                />
              </label>
              <label className="settings-label">
                Ubicación
                <input
                  className="settings-input"
                  value={form.JOB_LOCATION}
                  onChange={(e) => set("JOB_LOCATION", e.target.value)}
                  placeholder="Ej: Buenos Aires, Argentina"
                />
              </label>
              <label className="settings-label">
                Máximo de resultados
                <input
                  className="settings-input"
                  type="number"
                  min={5}
                  max={200}
                  value={form.JOB_MAX_RESULTS}
                  onChange={(e) => set("JOB_MAX_RESULTS", parseInt(e.target.value, 10) || 30)}
                />
              </label>
              <label className="settings-toggle-row">
                <span>Solo publicados hoy</span>
                <div
                  className={`settings-toggle ${form.JOB_SOLO_HOY ? "on" : ""}`}
                  onClick={() => set("JOB_SOLO_HOY", !form.JOB_SOLO_HOY)}
                >
                  <div className="settings-toggle-thumb" />
                </div>
              </label>
            </>
          )}

          {tab === "email" && (
            <>
              <label className="settings-label">
                Tu dirección de correo
                <input
                  className="settings-input"
                  type="email"
                  value={form.EMAIL_ADDRESS}
                  onChange={(e) => set("EMAIL_ADDRESS", e.target.value)}
                  placeholder="tucorreo@gmail.com"
                />
              </label>
              <label className="settings-label">
                Contraseña de aplicación
                <input
                  className="settings-input"
                  type="password"
                  value={form.EMAIL_PASSWORD}
                  onChange={(e) => set("EMAIL_PASSWORD", e.target.value)}
                  placeholder="contraseña de app de Gmail"
                />
              </label>
              <label className="settings-label">
                Ruta del CV
                <input
                  className="settings-input"
                  value={form.CV_FILE_PATH}
                  onChange={(e) => set("CV_FILE_PATH", e.target.value)}
                  placeholder="cv.pdf o C:\ruta\al\cv.pdf"
                />
              </label>
              <label className="settings-label">
                Asunto del correo
                <input
                  className="settings-input"
                  value={form.EMAIL_SUBJECT}
                  onChange={(e) => set("EMAIL_SUBJECT", e.target.value)}
                />
              </label>
              <label className="settings-label">
                Cuerpo del correo (plantilla)
                <small className="settings-hint">
                  Variables disponibles: {"{company_name}"}, {"{job_title}"}.<br/>
                  Si configurás la clave Gemini, la IA redactará automáticamente.
                </small>
                <textarea
                  className="settings-textarea"
                  rows={8}
                  value={form.EMAIL_BODY}
                  onChange={(e) => set("EMAIL_BODY", e.target.value)}
                />
              </label>

              <div className="settings-divider">Opciones avanzadas</div>
              
              <label className="settings-toggle-row">
                <span>Modo Dry Run (no envía emails reales)</span>
                <div
                  className={`settings-toggle ${form.DRY_RUN ? "on" : ""}`}
                  onClick={() => set("DRY_RUN", !form.DRY_RUN)}
                >
                  <div className="settings-toggle-thumb" />
                </div>
              </label>

              <div className="settings-divider">Tandas de envío</div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <label className="settings-label" style={{ flex: 1 }}>
                  Emails por tanda
                  <input
                    className="settings-input"
                    type="number"
                    min={1}
                    max={50}
                    value={form.EMAIL_BATCH_SIZE}
                    onChange={(e) => set("EMAIL_BATCH_SIZE", parseInt(e.target.value, 10) || 10)}
                  />
                </label>
                <label className="settings-label" style={{ flex: 1 }}>
                  Pausa entre tandas (seg)
                  <input
                    className="settings-input"
                    type="number"
                    min={10}
                    value={form.EMAIL_BATCH_PAUSE}
                    onChange={(e) => set("EMAIL_BATCH_PAUSE", parseInt(e.target.value, 10) || 300)}
                  />
                </label>
              </div>

              <label className="settings-toggle-row" style={{ marginTop: '1rem' }}>
                <span>Solo en horario laboral</span>
                <div
                  className={`settings-toggle ${form.EMAIL_BUSINESS_HOURS ? "on" : ""}`}
                  onClick={() => set("EMAIL_BUSINESS_HOURS", !form.EMAIL_BUSINESS_HOURS)}
                >
                  <div className="settings-toggle-thumb" />
                </div>
              </label>

              {form.EMAIL_BUSINESS_HOURS && (
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                  <label className="settings-label" style={{ flex: 1 }}>
                    Hora inicio (0-23)
                    <input
                      className="settings-input"
                      type="number"
                      min={0}
                      max={23}
                      value={form.EMAIL_BH_START}
                      onChange={(e) => set("EMAIL_BH_START", parseInt(e.target.value, 10) || 9)}
                    />
                  </label>
                  <label className="settings-label" style={{ flex: 1 }}>
                    Hora fin (0-23)
                    <input
                      className="settings-input"
                      type="number"
                      min={0}
                      max={23}
                      value={form.EMAIL_BH_END}
                      onChange={(e) => set("EMAIL_BH_END", parseInt(e.target.value, 10) || 18)}
                    />
                  </label>
                </div>
              )}
            </>
          )}

          {tab === "filters" && (
            <>
              <label className="settings-label">
                Modalidad de trabajo
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                  {[
                    { label: 'Todos', value: '' },
                    { label: 'Remoto', value: 'remoto' },
                    { label: 'Híbrido', value: 'hibrido' },
                    { label: 'Presencial', value: 'presencial' },
                  ].map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => set("JOB_MODALITY", opt.value)}
                      style={{
                        background: form.JOB_MODALITY === opt.value ? '#7c4dff' : 'rgba(255,255,255,0.06)',
                        border: `1px solid ${form.JOB_MODALITY === opt.value ? '#7c4dff' : 'rgba(255,255,255,0.1)'}`,
                        borderRadius: '8px',
                        padding: '6px 12px',
                        cursor: 'pointer',
                        color: form.JOB_MODALITY === opt.value ? '#fff' : '#888',
                        flex: 1
                      }}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </label>
              
              <label className="settings-label" style={{ marginTop: '1.5rem' }}>
                Palabras excluidas del título
                <small className="settings-hint">Una por línea. Ej: senior, líder, gerente</small>
                <textarea
                  className="settings-textarea"
                  rows={4}
                  value={form.EXCLUDE_KEYWORDS}
                  onChange={(e) => set("EXCLUDE_KEYWORDS", e.target.value)}
                  placeholder="senior&#10;líder&#10;manager"
                />
              </label>

              <label className="settings-label" style={{ marginTop: '1rem' }}>
                Empresas a ignorar (Blacklist)
                <small className="settings-hint">Una por línea. Ej: Consultora XYZ</small>
                <textarea
                  className="settings-textarea"
                  rows={4}
                  value={form.BLACKLIST_COMPANIES}
                  onChange={(e) => set("BLACKLIST_COMPANIES", e.target.value)}
                  placeholder="Empresa Mala S.A.&#10;Otra Consultora"
                />
              </label>
            </>
          )}

          {tab === "advanced" && (
            <>
              <label className="settings-label">
                Clave API de Gemini (para cartas personalizadas)
                <input
                  className="settings-input"
                  type="password"
                  value={form.GEMINI_API_KEY}
                  onChange={(e) => set("GEMINI_API_KEY", e.target.value)}
                  placeholder="AIza..."
                />
                <small className="settings-hint">
                  Opcional. Si la configurás, el Cartero usa Gemini AI para redactar
                  el cuerpo del email personalizado para cada empresa.
                </small>
              </label>
              <label className="settings-label">
                URL pública (para rastrear apertura de correos)
                <input
                  className="settings-input"
                  value={form.PUBLIC_URL}
                  onChange={(e) => set("PUBLIC_URL", e.target.value)}
                  placeholder="https://tudominio.com"
                />
                <small className="settings-hint">
                  Opcional. Si la configurás, se añade un píxel al email para saber
                  si el destinatario lo abrió. El backend debe ser accesible desde internet.
                </small>
              </label>

              <div className="settings-divider">Notificaciones Telegram</div>

              <label className="settings-label">
                Token del bot de Telegram
                <input
                  className="settings-input"
                  type="password"
                  value={form.TELEGRAM_TOKEN}
                  onChange={(e) => set("TELEGRAM_TOKEN", e.target.value)}
                  placeholder="123456789:ABCdef..."
                />
                <small className="settings-hint">
                  Creá un bot con @BotFather en Telegram y pegá el token acá.
                </small>
              </label>
              <label className="settings-label">
                Chat ID de Telegram
                <input
                  className="settings-input"
                  value={form.TELEGRAM_CHAT_ID}
                  onChange={(e) => set("TELEGRAM_CHAT_ID", e.target.value)}
                  placeholder="123456789"
                />
                <small className="settings-hint">
                  Tu chat ID (podés obtenerlo con @userinfobot). Recibirás alertas cuando el pipeline termine, haya respuestas o se abra un email.
                </small>
              </label>

              <div className="settings-divider">IMAP automático</div>

              <label className="settings-toggle-row">
                <span>Revisar bandeja automáticamente</span>
                <div
                  className={`settings-toggle ${form.IMAP_AUTO_ENABLED ? "on" : ""}`}
                  onClick={() => set("IMAP_AUTO_ENABLED", !form.IMAP_AUTO_ENABLED)}
                >
                  <div className="settings-toggle-thumb" />
                </div>
              </label>

              {form.IMAP_AUTO_ENABLED && (
                <label className="settings-label">
                  Intervalo de revisión (minutos)
                  <input
                    className="settings-input"
                    type="number"
                    min={5}
                    max={1440}
                    value={form.IMAP_INTERVAL_MINUTES}
                    onChange={(e) => set("IMAP_INTERVAL_MINUTES", parseInt(e.target.value, 10) || 30)}
                  />
                  <small className="settings-hint">
                    El sistema revisará tu bandeja de entrada cada N minutos buscando respuestas de las empresas.
                  </small>
                </label>
              )}

              <div className="settings-divider">Ejecución automática (Scheduler)</div>

              <label className="settings-toggle-row">
                <span>Activar búsqueda automática diaria</span>
                <div
                  className={`settings-toggle ${form.SCHEDULER_ENABLED ? "on" : ""}`}
                  onClick={() => set("SCHEDULER_ENABLED", !form.SCHEDULER_ENABLED)}
                >
                  <div className="settings-toggle-thumb" />
                </div>
              </label>

              {form.SCHEDULER_ENABLED && (
                <label className="settings-label">
                  Hora de ejecución
                  <input
                    className="settings-input"
                    type="time"
                    value={form.SCHEDULER_TIME}
                    onChange={(e) => set("SCHEDULER_TIME", e.target.value)}
                  />
                  <small className="settings-hint">
                    El sistema lanzará el pipeline completo (búsqueda + detective + cartero)
                    todos los días a esta hora, mientras el servidor esté corriendo.
                  </small>
                </label>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="settings-footer">
          <button className="settings-btn-cancel" onClick={onClose}>Cancelar</button>
          <button className={`settings-btn-save ${saved ? "saved" : ""}`} onClick={handleSave}>
            {saved ? "✓ Guardado" : "Guardar configuración"}
          </button>
        </div>
      </div>
    </div>
  );
}

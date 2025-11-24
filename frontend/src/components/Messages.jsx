import { useState, useEffect } from 'react'
import { messagesAPI } from '../services/api'

function Messages() {
  const [messages, setMessages] = useState([])
  const [threadId, setThreadId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ 
    content: '', 
    message_type: 'text',
    paths: []
  })

  const loadMessages = async (e) => {
    if (e) e.preventDefault()
    if (!threadId.trim()) {
      setError('Debes ingresar un Thread ID para cargar mensajes')
      return
    }
    try {
      setLoading(true)
      setError(null)
      const response = await messagesAPI.list(threadId)
      setMessages(response.data)
    } catch (err) {
      setError(err.response?.data?.detail?.error || err.response?.data?.detail || 'Error al cargar mensajes')
      setMessages([])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!threadId.trim()) {
      setError('Debes ingresar un Thread ID para enviar mensajes')
      return
    }
    try {
      setError(null)
      const payload = {
        content: formData.content,
        message_type: formData.message_type
      }
      if (formData.paths && formData.paths.length > 0) {
        payload.paths = formData.paths
      }
      await messagesAPI.create(threadId, payload)
      setFormData({ content: '', message_type: 'text', paths: [] })
      setShowForm(false)
      loadMessages()
    } catch (err) {
      setError(err.response?.data?.detail?.error || err.response?.data?.detail || 'Error al crear mensaje')
    }
  }

  const handleDelete = async (messageId) => {
    if (!confirm('¿Eliminar este mensaje?')) return
    try {
      setError(null)
      await messagesAPI.delete(threadId, messageId)
      loadMessages()
    } catch (err) {
      setError(err.response?.data?.detail?.error || 'Error al eliminar mensaje')
    }
  }

  return (
    <div>
      <div className="card">
        <h2>💬 Mensajes</h2>
        
        {error && (
          <div style={{ padding: '1rem', backgroundColor: '#fee', border: '1px solid #fcc', borderRadius: '4px', marginBottom: '1rem', color: '#c33' }}>
            {error}
          </div>
        )}

        {/* Formulario de búsqueda de thread */}
        <form onSubmit={loadMessages} style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#f8f9fa' }}>
          <div className="form-group" style={{ marginBottom: '0.5rem' }}>
            <label>🔍 Thread ID (UUID)</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                value={threadId}
                onChange={(e) => setThreadId(e.target.value)}
                placeholder="Ingresa el UUID del thread (ej: 550e8400-e29b-41d4-a716-446655440000)"
                disabled={loading}
                style={{ flex: 1 }}
              />
              <button type="submit" disabled={loading || !threadId.trim()}>
                {loading ? 'Cargando...' : 'Cargar Mensajes'}
              </button>
            </div>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#7f8c8d', marginTop: '0.5rem', marginBottom: 0 }}>
            El API de mensajes requiere un <strong>Thread ID</strong> (UUID) para cargar y enviar mensajes
          </p>
        </form>

        {threadId && (
          <button onClick={() => setShowForm(!showForm)} style={{ marginTop: '1rem' }}>
            {showForm ? 'Cancelar' : '+ Nuevo Mensaje'}
          </button>
        )}

        {showForm && threadId && (
          <form onSubmit={handleSubmit} style={{ marginTop: '1rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
            <div className="form-group">
              <label>Contenido del Mensaje *</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                required
                placeholder="Escribe tu mensaje..."
                rows="4"
              />
            </div>
            <div className="form-group">
              <label>Tipo de Mensaje</label>
              <select 
                value={formData.message_type}
                onChange={(e) => setFormData({ ...formData, message_type: e.target.value })}
              >
                <option value="text">📝 Texto</option>
                <option value="audio">🎵 Audio</option>
                <option value="file">📎 Archivo</option>
              </select>
            </div>
            <button type="submit">Enviar Mensaje</button>
          </form>
        )}
      </div>

      {threadId && messages.length > 0 && (
        <div className="card">
          <h3>Mensajes en el Thread</h3>
          <ul className="list">
            {messages.map((message) => (
              <li key={message.id} className="list-item">
                <div className="list-item-content">
                  <p style={{ fontWeight: '500', marginBottom: '0.5rem' }}>{message.content}</p>
                  <p style={{ fontSize: '0.8rem', color: '#95a5a6' }}>
                    Tipo: {message.type || 'text'} | ID: {message.id?.substring(0, 8)}...
                  </p>
                </div>
                <div className="list-item-actions">
                  <button className="danger" onClick={() => handleDelete(message.id)}>
                    Eliminar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {threadId && !loading && messages.length === 0 && (
        <div className="card empty">
          No hay mensajes en este thread. Crea el primero usando el botón "+ Nuevo Mensaje"
        </div>
      )}
    </div>
  )
}

export default Messages

import { useState } from 'react'
import { filesAPI } from '../services/api'

function Files() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [messageId, setMessageId] = useState('')
  const [threadId, setThreadId] = useState('')
  const [searchMessageId, setSearchMessageId] = useState('')
  const [searchThreadId, setSearchThreadId] = useState('')

  const loadFiles = async (e) => {
    if (e) e.preventDefault()
    
    if (!searchMessageId.trim() && !searchThreadId.trim()) {
      setError('Debes ingresar un Message ID o Thread ID para buscar archivos')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const params = {}
      if (searchMessageId.trim()) params.message_id = searchMessageId.trim()
      if (searchThreadId.trim()) params.thread_id = searchThreadId.trim()
      
      const response = await filesAPI.list(params)
      setFiles(response.data)
    } catch (err) {
      setError(err.response?.data?.detail?.error || err.response?.data?.detail || 'Error al cargar archivos')
      setFiles([])
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedFile) return

    if (!messageId.trim() && !threadId.trim()) {
      setError('Debes ingresar un Message ID o Thread ID para asociar el archivo')
      return
    }

    try {
      setError(null)
      const formData = new FormData()
      formData.append('file', selectedFile)
      if (messageId.trim()) formData.append('message_id', messageId.trim())
      if (threadId.trim()) formData.append('thread_id', threadId.trim())

      await filesAPI.upload(formData)
      setSelectedFile(null)
      setMessageId('')
      setThreadId('')
      setShowForm(false)
      alert('Archivo subido exitosamente')
    } catch (err) {
      setError(err.response?.data?.detail?.error || err.response?.data?.detail || 'Error al subir archivo')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar este archivo?')) return
    try {
      setError(null)
      await filesAPI.delete(id)
      alert('Archivo eliminado exitosamente')
      loadFiles()
    } catch (err) {
      setError(err.response?.data?.detail?.error || 'Error al eliminar archivo')
    }
  }

  const handleDownload = async (id, filename) => {
    try {
      const response = await filesAPI.getDownloadUrl(id)
      const url = response.data.url || response.data.download_url
      if (url) {
        window.open(url, '_blank')
      } else {
        setError('No se pudo obtener URL de descarga')
      }
    } catch (err) {
      setError(err.response?.data?.detail?.error || 'Error al obtener URL de descarga')
    }
  }

  if (loading) return <div className="loading">Cargando archivos...</div>

  return (
    <div>
      <div className="card">
        <h2>📁 Archivos</h2>

        {error && (
          <div style={{ padding: '1rem', backgroundColor: '#fee', border: '1px solid #fcc', borderRadius: '4px', marginBottom: '1rem', color: '#c33' }}>
            {error}
          </div>
        )}

        {/* Formulario de búsqueda */}
        <form onSubmit={loadFiles} style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#f8f9fa' }}>
          <div className="form-group" style={{ marginBottom: '0.5rem' }}>
            <label>🔍 Buscar Archivos</label>
            <input
              type="text"
              value={searchMessageId}
              onChange={(e) => setSearchMessageId(e.target.value)}
              placeholder="Message ID (opcional)"
              disabled={loading}
              style={{ marginBottom: '0.5rem' }}
            />
            <input
              type="text"
              value={searchThreadId}
              onChange={(e) => setSearchThreadId(e.target.value)}
              placeholder="Thread ID (opcional)"
              disabled={loading}
            />
          </div>
          <button type="submit" disabled={loading || (!searchMessageId.trim() && !searchThreadId.trim())}>
            {loading ? 'Buscando...' : 'Buscar Archivos'}
          </button>
          <p style={{ fontSize: '0.85rem', color: '#7f8c8d', marginTop: '0.5rem', marginBottom: 0 }}>
            Debes ingresar al menos un <strong>Message ID</strong> o <strong>Thread ID</strong> para buscar archivos
          </p>
        </form>

        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancelar' : '+ Subir Archivo'}
        </button>

        {showForm && (
          <form onSubmit={handleSubmit} style={{ marginTop: '1rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
            <div className="form-group">
              <label>Archivo *</label>
              <input
                type="file"
                onChange={handleFileChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Message ID</label>
              <input
                type="text"
                value={messageId}
                onChange={(e) => setMessageId(e.target.value)}
                placeholder="ID del mensaje (opcional si hay thread_id)"
              />
            </div>
            <div className="form-group">
              <label>Thread ID</label>
              <input
                type="text"
                value={threadId}
                onChange={(e) => setThreadId(e.target.value)}
                placeholder="ID del thread (opcional si hay message_id)"
              />
            </div>
            <p style={{ fontSize: '0.85rem', color: '#e67e22', marginBottom: '1rem' }}>
              ⚠️ Al menos uno de los dos IDs es requerido
            </p>
            <button type="submit" disabled={!selectedFile || (!messageId.trim() && !threadId.trim())}>
              Subir Archivo
            </button>
          </form>
        )}
      </div>

      {files.length > 0 && (
        <div className="card">
          <h3>Archivos Encontrados</h3>
          <ul className="list">
            {files.map((file) => (
              <li key={file.id} className="list-item">
                <div className="list-item-content">
                  <h3>{file.filename || file.original_filename}</h3>
                  <p>Tamaño: {(file.size / 1024).toFixed(2)} KB</p>
                  {file.message_id && <p>Message ID: {file.message_id}</p>}
                  {file.thread_id && <p>Thread ID: {file.thread_id}</p>}
                </div>
                <div className="list-item-actions">
                  <button onClick={() => handleDownload(file.id, file.filename)}>
                    Descargar
                  </button>
                  <button className="danger" onClick={() => handleDelete(file.id)}>
                    Eliminar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default Files

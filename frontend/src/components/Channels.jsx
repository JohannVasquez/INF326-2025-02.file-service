import { useState } from 'react'
import { channelsAPI } from '../services/api'

function Channels() {
  const [channels, setChannels] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [ownerId, setOwnerId] = useState('')
  const [formData, setFormData] = useState({ 
    name: '', 
    owner_id: '', 
    users: '', 
    channel_type: 'public' 
  })

  const loadChannels = async (e) => {
    if (e) e.preventDefault()
    if (!ownerId.trim()) {
      setError('Debes ingresar un Owner ID para buscar canales')
      return
    }
    try {
      setLoading(true)
      setError(null)
      const response = await channelsAPI.listByOwner(ownerId)
      setChannels(response.data)
    } catch (err) {
      setError(err.response?.data?.detail?.message || err.response?.data?.detail || 'Error al cargar canales')
      setChannels([])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError(null)
      // Convertir users de string a array
      const payload = {
        ...formData,
        users: formData.users.split(',').map(u => u.trim()).filter(u => u)
      }
      await channelsAPI.create(payload)
      setFormData({ name: '', owner_id: '', users: '', channel_type: 'public' })
      setShowForm(false)
      if (ownerId) loadChannels()
    } catch (err) {
      setError(err.response?.data?.detail?.message || err.response?.data?.detail?.error || 'Error al crear canal')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar este canal?')) return
    try {
      setError(null)
      await channelsAPI.delete(id)
      loadChannels()
    } catch (err) {
      setError(err.response?.data?.detail?.error || 'Error al eliminar canal')
    }
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2>Canales</h2>
          <button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancelar' : '➕ Nuevo Canal'}
          </button>
        </div>

        {error && (
          <div style={{ padding: '1rem', backgroundColor: '#fee', border: '1px solid #fcc', borderRadius: '4px', marginBottom: '1rem', color: '#c33' }}>
            {error}
          </div>
        )}

        {/* Formulario de búsqueda por owner */}
        <form onSubmit={loadChannels} style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#f8f9fa' }}>
          <div className="form-group" style={{ marginBottom: '0.5rem' }}>
            <label>🔍 Buscar Canales por Owner ID</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                value={ownerId}
                onChange={(e) => setOwnerId(e.target.value)}
                placeholder="Ingresa el ID del propietario"
                disabled={loading}
              />
              <button type="submit" disabled={loading || !ownerId.trim()}>
                {loading ? 'Buscando...' : 'Buscar'}
              </button>
            </div>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#7f8c8d', marginTop: '0.5rem' }}>
            La API del servicio de canales requiere un Owner ID para listar canales
          </p>
        </form>

        {showForm && (
          <form onSubmit={handleSubmit} style={{ marginTop: '1rem', padding: '1.5rem', border: '2px solid #27ae60', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
            <h3 style={{ marginBottom: '1rem', color: '#2c3e50' }}>➕ Crear Nuevo Canal</h3>
            <div className="form-group">
              <label>Nombre del Canal *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="Mi Canal"
              />
            </div>
            <div className="form-group">
              <label>Owner ID *</label>
              <input
                type="text"
                value={formData.owner_id}
                onChange={(e) => setFormData({ ...formData, owner_id: e.target.value })}
                required
                placeholder="ID del propietario"
              />
            </div>
            <div className="form-group">
              <label>Usuarios (separados por comas) *</label>
              <input
                type="text"
                value={formData.users}
                onChange={(e) => setFormData({ ...formData, users: e.target.value })}
                required
                placeholder="user1, user2, user3"
              />
              <small style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
                Lista de IDs de usuarios separados por comas
              </small>
            </div>
            <div className="form-group">
              <label>Tipo de Canal</label>
              <select
                value={formData.channel_type}
                onChange={(e) => setFormData({ ...formData, channel_type: e.target.value })}
              >
                <option value="public">Público</option>
                <option value="private">Privado</option>
              </select>
            </div>
            <button type="submit">Crear Canal</button>
          </form>
        )}
      </div>

      {channels.length > 0 && (
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Resultados ({channels.length})</h3>
          <ul className="list">
            {channels.map((channel) => (
              <li key={channel.id || channel._id} className="list-item">
                <div className="list-item-content">
                  <h3>{channel.name}</h3>
                  {channel.description && <p>{channel.description}</p>}
                  {channel.owner_id && <p style={{ fontSize: '0.85rem', color: '#7f8c8d' }}>Owner: {channel.owner_id}</p>}
                </div>
                <div className="list-item-actions">
                  <button className="danger" onClick={() => handleDelete(channel.id || channel._id)}>
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

export default Channels

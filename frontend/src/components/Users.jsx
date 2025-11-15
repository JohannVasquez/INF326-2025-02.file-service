import { useState } from 'react'
import { usersAPI } from '../services/api'

function Users() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [showLogin, setShowLogin] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: ''
  })
  const [loginData, setLoginData] = useState({
    username_or_email: '',
    password: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validaciones locales
    if (formData.username.length < 3 || formData.username.length > 50) {
      setError('El username debe tener entre 3 y 50 caracteres')
      return
    }
    if (formData.password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres')
      return
    }
    
    try {
      setLoading(true)
      setError(null)
      setSuccess(null)
      await usersAPI.create(formData)
      setFormData({ username: '', email: '', password: '', full_name: '' })
      setShowForm(false)
      setSuccess('✅ Usuario registrado correctamente. Puedes iniciar sesión.')
    } catch (err) {
      const errorMsg = err.response?.data?.detail?.message 
        || err.response?.data?.detail 
        || err.response?.data?.error
        || err.message
        || 'Error al crear usuario'
      setError('❌ ' + errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      setLoading(true)
      setError(null)
      setSuccess(null)
      const response = await usersAPI.login(loginData)
      setLoginData({ username_or_email: '', password: '' })
      setShowLogin(false)
      setSuccess('✅ Login exitoso! Token: ' + JSON.stringify(response.data, null, 2))
    } catch (err) {
      setError(err.response?.data?.detail?.message || err.response?.data?.detail?.error || err.response?.data?.detail || 'Error al autenticar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2>Gestión de Usuarios</h2>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button onClick={() => { setShowLogin(!showLogin); setShowForm(false); }}>
              {showLogin ? 'Cancelar' : '🔐 Login'}
            </button>
            <button onClick={() => { setShowForm(!showForm); setShowLogin(false); }}>
              {showForm ? 'Cancelar' : '➕ Registrar'}
            </button>
          </div>
        </div>

        {error && (
          <div style={{ padding: '1rem', backgroundColor: '#fee', border: '1px solid #fcc', borderRadius: '4px', marginBottom: '1rem', color: '#c33' }}>
            {error}
          </div>
        )}

        {success && (
          <div style={{ padding: '1rem', backgroundColor: '#efe', border: '1px solid #cfc', borderRadius: '4px', marginBottom: '1rem', color: '#3c3', whiteSpace: 'pre-wrap' }}>
            {success}
          </div>
        )}

        {showLogin && (
          <form onSubmit={handleLogin} style={{ marginBottom: '1rem', padding: '1.5rem', border: '2px solid #3498db', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
            <h3 style={{ marginBottom: '1rem', color: '#2c3e50' }}>🔐 Iniciar Sesión</h3>
            <div className="form-group">
              <label>Username o Email</label>
              <input
                type="text"
                value={loginData.username_or_email}
                onChange={(e) => setLoginData({ ...loginData, username_or_email: e.target.value })}
                required
                disabled={loading}
                placeholder="usuario o email@ejemplo.com"
              />
              <small style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
                Puedes usar tu username o email para iniciar sesión
              </small>
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                required
                disabled={loading}
              />
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'Autenticando...' : 'Iniciar Sesión'}
            </button>
          </form>
        )}

        {showForm && (
          <form onSubmit={handleSubmit} style={{ marginBottom: '1rem', padding: '1.5rem', border: '2px solid #27ae60', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
            <h3 style={{ marginBottom: '1rem', color: '#2c3e50' }}>➕ Registrar Nuevo Usuario</h3>
            <div className="form-group">
              <label>Username *</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
                disabled={loading}
                placeholder="nombre_usuario"
                minLength={3}
                maxLength={50}
              />
              <small style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
                Entre 3 y 50 caracteres
              </small>
            </div>
            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                disabled={loading}
                placeholder="usuario@ejemplo.com"
              />
            </div>
            <div className="form-group">
              <label>Password *</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                disabled={loading}
                placeholder="Contraseña segura"
                minLength={8}
              />
              <small style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
                Mínimo 8 caracteres
              </small>
            </div>
            <div className="form-group">
              <label>Nombre Completo (opcional)</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                disabled={loading}
                placeholder="Juan Pérez"
              />
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'Creando...' : 'Crear Usuario'}
            </button>
          </form>
        )}

        {!showForm && !showLogin && (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#7f8c8d' }}>
            <p style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
              👥 Sistema de Gestión de Usuarios
            </p>
            <p style={{ marginBottom: '0.5rem' }}>
              📝 <strong>Registra</strong> un nuevo usuario para el sistema
            </p>
            <p>
              🔐 <strong>Inicia sesión</strong> con tus credenciales
            </p>
            <p style={{ marginTop: '1.5rem', fontSize: '0.9rem', fontStyle: 'italic' }}>
              Nota: La API del servicio de usuarios no provee endpoints públicos para listar todos los usuarios.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Users

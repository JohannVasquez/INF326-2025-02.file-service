import { useState } from 'react'
import { searchAPI } from '../services/api'

function Search() {
  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState('all')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    try {
      setLoading(true)
      setError(null)
      let response

      switch (searchType) {
        case 'messages':
          response = await searchAPI.searchMessages(query)
          break
        case 'files':
          response = await searchAPI.searchFiles(query)
          break
        default:
          response = await searchAPI.search(query)
      }

      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail?.error || 'Error en la búsqueda')
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card">
        <h2>Búsqueda</h2>
        <form onSubmit={handleSearch}>
          <div className="form-group">
            <label>Tipo de Búsqueda</label>
            <select 
              value={searchType} 
              onChange={(e) => setSearchType(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', borderRadius: '4px', border: '1px solid #ddd' }}
            >
              <option value="all">Todo</option>
              <option value="messages">Mensajes</option>
              <option value="files">Archivos</option>
            </select>
          </div>

          <div className="search-box">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar..."
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
          </div>
        </form>

        {error && <div className="error">{error}</div>}
      </div>

      {results && (
        <div className="card">
          <h3>Resultados ({Array.isArray(results) ? results.length : 0})</h3>
          
          {!results || (Array.isArray(results) && results.length === 0) ? (
            <div className="empty">No se encontraron resultados</div>
          ) : Array.isArray(results) ? (
            <ul className="list">
              {results.map((item, index) => (
                <li key={item.id || index} className="list-item">
                  <div className="list-item-content">
                    <h3>{item.filename || item.content || item.name || 'Resultado'}</h3>
                    {item.content && <p>{item.content.substring(0, 150)}...</p>}
                    {item.type && <p style={{ color: '#7f8c8d' }}>Tipo: {item.type}</p>}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="empty">Formato de resultados inesperado</div>
          )}
        </div>
      )}
    </div>
  )
}

export default Search

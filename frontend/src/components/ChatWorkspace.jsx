import { useEffect, useMemo, useState } from 'react'
import {
  usersAPI,
  channelsAPI,
  threadsAPI,
  messagesAPI,
  filesAPI,
  searchAPI,
  moderationAPI,
  presenceAPI,
  wikiAPI,
  programmingChatAPI,
  setAuthToken,
} from '../services/api'

const isBrowser = typeof window !== 'undefined'

const resolveChannelId = (channel) => channel?.id || channel?._id || channel?.channel_id || channel?.owner_id
const resolveThreadId = (thread) => thread?.uuid || thread?.thread_id || thread?.id
const normalizeList = (payload) => {
  if (Array.isArray(payload)) return payload
  if (payload?.items && Array.isArray(payload.items)) return payload.items
  if (payload?.data && Array.isArray(payload.data)) return payload.data
  return []
}
const loadStoredSession = () => {
  if (!isBrowser) return null
  const raw = localStorage.getItem('chatUser')
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw)
    return parsed?.token && parsed?.user ? parsed : null
  } catch (_) {
    return null
  }
}

function ChatWorkspace() {
  const [session, setSession] = useState(loadStoredSession)
  const [showRegister, setShowRegister] = useState(false)
  const [loginForm, setLoginForm] = useState({ username_or_email: '', password: '' })
  const [registerForm, setRegisterForm] = useState({ username: '', email: '', password: '', full_name: '' })
  const [channels, setChannels] = useState([])
  const [channelFilter, setChannelFilter] = useState('')
  const [selectedChannel, setSelectedChannel] = useState(null)
  const [threads, setThreads] = useState([])
  const [selectedThread, setSelectedThread] = useState(null)
  const [newThreadName, setNewThreadName] = useState('')
  const [messages, setMessages] = useState([])
  const [attachments, setAttachments] = useState([])
  const [presenceUsers, setPresenceUsers] = useState([])
  const [presenceStats, setPresenceStats] = useState(null)
  const [searchFilters, setSearchFilters] = useState({ scope: 'messages', query: '' })
  const [searchResults, setSearchResults] = useState(null)
  const [wikiQuestion, setWikiQuestion] = useState('')
  const [wikiAnswer, setWikiAnswer] = useState('')
  const [devQuestion, setDevQuestion] = useState('')
  const [devAnswer, setDevAnswer] = useState('')
  const [composer, setComposer] = useState({ content: '', messageType: 'text', attachment: null })
  const [loading, setLoading] = useState({ channels: false, threads: false, messages: false, sending: false })
  const [statusMessage, setStatusMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const channelId = resolveChannelId(selectedChannel)
  const threadId = resolveThreadId(selectedThread)

  useEffect(() => {
    if (session?.token) {
      setAuthToken(session.token)
    }
  }, [session])

  useEffect(() => {
    loadChannels()
  }, [])

  useEffect(() => {
    if (!channelId) {
      setThreads([])
      setSelectedThread(null)
      return
    }
    loadThreads(channelId)
  }, [channelId])

  useEffect(() => {
    if (!threadId) {
      setMessages([])
      setAttachments([])
      return
    }
    loadMessages(threadId)
    loadAttachments(threadId)
  }, [threadId])

  useEffect(() => {
    refreshPresence()
    const interval = setInterval(refreshPresence, 45000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (!session?.user?.id) return
    const registerPresence = async () => {
      try {
        await presenceAPI.register({ user_id: session.user.id, device: 'web' })
      } catch (_) {
        // noop
      }
    }
    registerPresence()
    const heartbeat = setInterval(() => {
      presenceAPI.update(session.user.id, { heartbeat: true }).catch(() => {})
    }, 60000)
    return () => clearInterval(heartbeat)
  }, [session])

  const filteredChannels = useMemo(() => {
    if (!channelFilter.trim()) return channels
    return channels.filter((channel) =>
      channel?.name?.toLowerCase().includes(channelFilter.toLowerCase()) ||
      resolveChannelId(channel)?.toLowerCase().includes(channelFilter.toLowerCase())
    )
  }, [channels, channelFilter])

  const handleLogin = async (event) => {
    event.preventDefault()
    setErrorMessage('')
    setStatusMessage('')
    try {
      const { data: tokenData } = await usersAPI.login(loginForm)
      setAuthToken(tokenData.access_token)
      const { data: profile } = await usersAPI.me()
      const newSession = { token: tokenData.access_token, user: profile }
      setSession(newSession)
      if (isBrowser) {
        localStorage.setItem('chatUser', JSON.stringify(newSession))
      }
      setStatusMessage('✅ Sesión iniciada')
      setLoginForm({ username_or_email: '', password: '' })
    } catch (error) {
      const errorDetail = error.response?.data?.detail
      let errorMsg = 'Error al iniciar sesión'
      
      if (typeof errorDetail === 'object' && errorDetail?.error) {
        errorMsg = errorDetail.error
      } else if (typeof errorDetail === 'string') {
        errorMsg = errorDetail
      } else if (error.message) {
        errorMsg = error.message
      }
      
      // Detectar error 403
      if (error.response?.status === 403) {
        errorMsg = '❌ Error 403: El servicio de usuarios rechazó la petición. Verifica que el usuario exista y esté activo.'
      }
      
      setErrorMessage(errorMsg)
    }
  }

  const handleRegister = async (event) => {
    event.preventDefault()
    setErrorMessage('')
    setStatusMessage('')
    try {
      await usersAPI.create(registerForm)
      setStatusMessage('✅ Usuario registrado. Ahora puedes iniciar sesión')
      setRegisterForm({ username: '', email: '', password: '', full_name: '' })
      setShowRegister(false)
    } catch (error) {
      const errorDetail = error.response?.data?.detail
      let errorMsg = 'Error al registrar usuario'
      
      if (typeof errorDetail === 'object' && errorDetail?.error) {
        errorMsg = errorDetail.error
      } else if (typeof errorDetail === 'string') {
        errorMsg = errorDetail
      } else if (error.message) {
        errorMsg = error.message
      }
      
      setErrorMessage(errorMsg)
    }
  }

  const handleLogout = async () => {
    if (session?.user?.id) {
      await presenceAPI.update(session.user.id, { status: 'offline' }).catch(() => {})
    }
    setSession(null)
    setAuthToken(null)
    if (isBrowser) {
      localStorage.removeItem('chatUser')
    }
    setStatusMessage('Cerraste sesión')
  }

  const loadChannels = async () => {
    setLoading((prev) => ({ ...prev, channels: true }))
    setErrorMessage('')
    try {
      const { data } = await channelsAPI.list({ page_size: 50 })
      const nextChannels = normalizeList(data)
      setChannels(nextChannels)
      if (!selectedChannel && nextChannels.length) {
        setSelectedChannel(nextChannels[0])
      }
    } catch (error) {
      setErrorMessage('No se pudieron cargar los canales')
    } finally {
      setLoading((prev) => ({ ...prev, channels: false }))
    }
  }

  const loadThreads = async (channel) => {
    setLoading((prev) => ({ ...prev, threads: true }))
    setErrorMessage('')
    try {
      const { data } = await threadsAPI.listByChannel(channel)
      const list = normalizeList(data)
      setThreads(list)
      if (!threadId && list.length) {
        setSelectedThread(list[0])
      }
    } catch (error) {
      setErrorMessage('No se pudieron cargar los hilos de este canal')
    } finally {
      setLoading((prev) => ({ ...prev, threads: false }))
    }
  }

  const loadMessages = async (thread) => {
    setLoading((prev) => ({ ...prev, messages: true }))
    setErrorMessage('')
    try {
      const { data } = await messagesAPI.list(thread, { limit: 100 })
      setMessages(normalizeList(data))
    } catch (error) {
      setErrorMessage('No se pudieron cargar los mensajes')
    } finally {
      setLoading((prev) => ({ ...prev, messages: false }))
    }
  }

  const loadAttachments = async (thread) => {
    try {
      const { data } = await filesAPI.list({ thread_id: thread })
      setAttachments(Array.isArray(data) ? data : [])
    } catch (_) {
      setAttachments([])
    }
  }

  const refreshPresence = async () => {
    try {
      const [usersResp, statsResp] = await Promise.all([
        presenceAPI.list('online'),
        presenceAPI.stats(),
      ])
      const list = Array.isArray(usersResp?.data) ? usersResp.data : normalizeList(usersResp)
      setPresenceUsers(list)
      setPresenceStats(statsResp?.data || statsResp)
    } catch (_) {
      // ignore presence errors to avoid UI noise
    }
  }

  const handleCreateThread = async (event) => {
    event.preventDefault()
    if (!newThreadName.trim() || !channelId || !session?.user?.id) {
      setErrorMessage('Selecciona un canal e inicia sesión para crear hilos')
      return
    }
    try {
      await threadsAPI.create({ channel_id: channelId, thread_name: newThreadName.trim(), user_id: session.user.id })
      setNewThreadName('')
      loadThreads(channelId)
      setStatusMessage('Hilo creado exitosamente')
    } catch (error) {
      setErrorMessage('No se pudo crear el hilo')
    }
  }

  const handleSendMessage = async (event) => {
    event.preventDefault()
    if (!session?.user?.id) {
      setErrorMessage('Debes iniciar sesión para enviar mensajes')
      return
    }
    if (!threadId || !channelId) {
      setErrorMessage('Selecciona un canal y un hilo para enviar mensajes')
      return
    }
    if (!composer.content.trim()) {
      setErrorMessage('Escribe un mensaje antes de enviarlo')
      return
    }
    setLoading((prev) => ({ ...prev, sending: true }))
    setErrorMessage('')
    try {
      const moderation = await moderationAPI.check({
        user_id: session.user.id,
        channel_id: channelId,
        content: composer.content.trim(),
      })
      if (moderation?.data && moderation.data.is_approved === false) {
        setErrorMessage(moderation.data.message || 'La moderación bloqueó este mensaje')
        setLoading((prev) => ({ ...prev, sending: false }))
        return
      }
      const response = await messagesAPI.create(threadId, {
        content: composer.content.trim(),
        message_type: composer.messageType,
      }, session.user.id)
      const createdMessage = response?.data || response
      if (composer.attachment) {
        const formData = new FormData()
        formData.append('file', composer.attachment)
        formData.append('thread_id', threadId)
        if (createdMessage?.id) {
          formData.append('message_id', createdMessage.id)
        }
        await filesAPI.upload(formData)
      }
      setComposer({ content: '', messageType: 'text', attachment: null })
      loadMessages(threadId)
      loadAttachments(threadId)
    } catch (error) {
      setErrorMessage('No se pudo enviar el mensaje')
    } finally {
      setLoading((prev) => ({ ...prev, sending: false }))
    }
  }

  const handleSearch = async (event) => {
    event.preventDefault()
    if (!searchFilters.query.trim()) return
    setErrorMessage('')
    try {
      let response
      const params = {}
      if (channelId) params.channel_id = channelId
      if (threadId) params.thread_id = threadId
      switch (searchFilters.scope) {
        case 'files':
          response = await searchAPI.searchFiles(searchFilters.query, params)
          break
        case 'channels':
          response = await searchAPI.searchChannels(searchFilters.query, params)
          break
        case 'all':
          response = await searchAPI.global(searchFilters.query, params)
          break
        case 'messages':
        default:
          response = await searchAPI.searchMessages(searchFilters.query, params)
          break
      }
      setSearchResults({ scope: searchFilters.scope, data: response?.data || response })
    } catch (error) {
      setErrorMessage('La búsqueda falló, intenta nuevamente')
    }
  }

  const askWiki = async (event) => {
    event.preventDefault()
    if (!wikiQuestion.trim()) return
    try {
      const { data } = await wikiAPI.ask(wikiQuestion.trim())
      setWikiAnswer(data?.message || 'Sin respuesta')
    } catch (error) {
      setWikiAnswer('Error consultando al bot de Wikipedia')
    }
  }

  const askDevBot = async (event) => {
    event.preventDefault()
    if (!devQuestion.trim()) return
    try {
      const { data } = await programmingChatAPI.ask(devQuestion.trim())
      setDevAnswer(data?.reply || 'Sin respuesta')
    } catch (error) {
      setDevAnswer('El bot de programación no respondió')
    }
  }

  const presenceList = useMemo(() => {
    if (Array.isArray(presenceUsers)) return presenceUsers
    if (presenceUsers?.users) return presenceUsers.users
    return []
  }, [presenceUsers])

  return (
    <div className="chat-layout">
      <section className="chat-sidebar">
        <div className="card">
          <h2>Cuenta</h2>
          {errorMessage && <div className="error">{errorMessage}</div>}
          {session?.user ? (
            <>
              <p><strong>Usuario:</strong> {session.user.username}</p>
              <p><strong>Email:</strong> {session.user.email}</p>
              <button onClick={handleLogout}>Cerrar sesión</button>
            </>
          ) : showRegister ? (
            <>
              <form onSubmit={handleRegister} className="stacked-form">
                <input
                  type="text"
                  placeholder="Nombre de usuario"
                  value={registerForm.username}
                  onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={registerForm.email}
                  onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                  required
                />
                <input
                  type="text"
                  placeholder="Nombre completo (opcional)"
                  value={registerForm.full_name}
                  onChange={(e) => setRegisterForm({ ...registerForm, full_name: e.target.value })}
                />
                <input
                  type="password"
                  placeholder="Contraseña"
                  value={registerForm.password}
                  onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                  required
                />
                <button type="submit">Registrarse</button>
                <button type="button" className="secondary" onClick={() => setShowRegister(false)}>
                  Volver a iniciar sesión
                </button>
              </form>
            </>
          ) : (
            <>
              <form onSubmit={handleLogin} className="stacked-form">
                <input
                  type="text"
                  placeholder="Usuario o email"
                  value={loginForm.username_or_email}
                  onChange={(e) => setLoginForm({ ...loginForm, username_or_email: e.target.value })}
                  required
                />
                <input
                  type="password"
                  placeholder="Contraseña"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  required
                />
                <button type="submit">Iniciar sesión</button>
                <button type="button" className="secondary" onClick={() => setShowRegister(true)}>
                  Crear cuenta nueva
                </button>
              </form>
            </>
          )}
          {statusMessage && <p className="status-message">{statusMessage}</p>}
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Canales</h3>
            <button onClick={loadChannels} disabled={loading.channels}>Actualizar</button>
          </div>
          <input
            type="text"
            placeholder="Buscar canal"
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
          />
          <ul className="list scrollable">
            {filteredChannels.map((channel) => (
              <li
                key={resolveChannelId(channel)}
                className={resolveChannelId(channel) === channelId ? 'active' : ''}
                onClick={() => setSelectedChannel(channel)}
              >
                <p className="item-title">{channel?.name || 'Canal sin nombre'}</p>
                <small>{resolveChannelId(channel)}</small>
              </li>
            ))}
            {!filteredChannels.length && <li>No hay canales disponibles</li>}
          </ul>
        </div>

        <div className="card">
          <h3>Presencia</h3>
          {presenceStats && (
            <p className="presence-meta">Online: {presenceStats?.online ?? presenceList.length} · Offline: {presenceStats?.offline ?? 'N/D'}</p>
          )}
          <ul className="list scrollable">
            {presenceList.map((item) => (
              <li key={item.userId || item.user_id}>
                <p className="item-title">{item.userId || item.user_id}</p>
                <small>{item.status || 'online'} · {item.device || 'web'}</small>
              </li>
            ))}
            {!presenceList.length && <li>Sin usuarios conectados</li>}
          </ul>
        </div>
      </section>

      <section className="chat-main">
        <div className="card">
          <div className="card-header">
            <h2>{selectedChannel?.name || 'Selecciona un canal'}</h2>
            {channelId && (
              <form onSubmit={handleCreateThread} className="inline-form">
                <input
                  type="text"
                  placeholder="Nuevo hilo"
                  value={newThreadName}
                  onChange={(e) => setNewThreadName(e.target.value)}
                />
                <button type="submit">Crear</button>
              </form>
            )}
          </div>
          <ul className="pill-list">
            {threads.map((thread) => (
              <li
                key={resolveThreadId(thread)}
                className={resolveThreadId(thread) === threadId ? 'active' : ''}
                onClick={() => setSelectedThread(thread)}
              >
                {thread?.title || thread?.thread_name || 'Hilo'}
              </li>
            ))}
            {!threads.length && <li>No hay hilos para este canal</li>}
          </ul>
        </div>

        <div className="card messages-card">
          <div className="card-header">
            <h3>Mensajes</h3>
            {loading.messages && <span>Cargando...</span>}
          </div>
          <div className="messages-list">
            {messages.map((message) => (
              <div key={message.id} className="message-row">
                <div className="message-meta">
                  <strong>{message.user_id || message.author || 'Usuario'}</strong>
                  <small>{new Date(message.created_at || Date.now()).toLocaleString()}</small>
                </div>
                <p>{message.content}</p>
                <small>Tipo: {message.type || message.message_type || 'text'}</small>
              </div>
            ))}
            {!messages.length && <p className="empty">No hay mensajes en este hilo</p>}
          </div>
        </div>

        <form className="card composer" onSubmit={handleSendMessage}>
          <textarea
            placeholder="Escribe un mensaje..."
            value={composer.content}
            onChange={(e) => setComposer({ ...composer, content: e.target.value })}
          />
          <div className="composer-actions">
            <select
              value={composer.messageType}
              onChange={(e) => setComposer({ ...composer, messageType: e.target.value })}
            >
              <option value="text">Texto</option>
              <option value="audio">Audio</option>
              <option value="file">Archivo</option>
            </select>
            <input
              type="file"
              onChange={(e) => setComposer({ ...composer, attachment: e.target.files?.[0] || null })}
            />
            <button type="submit" disabled={loading.sending}>
              {loading.sending ? 'Enviando...' : 'Enviar'}
            </button>
          </div>
        </form>
      </section>

      <section className="chat-utility">
        <div className="card">
          <h3>Búsqueda</h3>
          <form onSubmit={handleSearch} className="stacked-form">
            <select
              value={searchFilters.scope}
              onChange={(e) => setSearchFilters({ ...searchFilters, scope: e.target.value })}
            >
              <option value="messages">Mensajes</option>
              <option value="files">Archivos</option>
              <option value="channels">Canales</option>
              <option value="all">Todo</option>
            </select>
            <input
              type="text"
              placeholder="Buscar..."
              value={searchFilters.query}
              onChange={(e) => setSearchFilters({ ...searchFilters, query: e.target.value })}
            />
            <button type="submit">Buscar</button>
          </form>
          {searchResults && (
            <div className="search-results">
              <h4>Resultados ({searchFilters.scope})</h4>
              {searchFilters.scope === 'all' ? (
                <pre>{JSON.stringify(searchResults.data, null, 2)}</pre>
              ) : Array.isArray(searchResults.data) ? (
                <ul className="list scrollable">
                  {searchResults.data.map((item) => (
                    <li key={item.id || item.thread_id || item.filename}>
                      <p className="item-title">{item.title || item.filename || item.content || 'Resultado'}</p>
                      {item.content && <small>{item.content.slice(0, 140)}...</small>}
                    </li>
                  ))}
                </ul>
              ) : (
                <pre>{JSON.stringify(searchResults.data, null, 2)}</pre>
              )}
            </div>
          )}
        </div>

        <div className="card">
          <h3>Archivos del hilo</h3>
          <ul className="list scrollable">
            {attachments.map((file) => (
              <li key={file.id}>
                <p className="item-title">{file.filename || file.original_filename}</p>
                <small>{((file.size || 0) / 1024).toFixed(1)} KB</small>
              </li>
            ))}
            {!attachments.length && <li>No hay archivos asociados</li>}
          </ul>
        </div>

        <div className="card">
          <h3>WikipediBot</h3>
          <form onSubmit={askWiki} className="stacked-form">
            <input
              type="text"
              value={wikiQuestion}
              onChange={(e) => setWikiQuestion(e.target.value)}
              placeholder="¿Qué quieres saber?"
            />
            <button type="submit">Preguntar</button>
          </form>
          {wikiAnswer && <p className="bot-reply">{wikiAnswer}</p>}
        </div>

        <div className="card">
          <h3>DevBot</h3>
          <form onSubmit={askDevBot} className="stacked-form">
            <input
              type="text"
              value={devQuestion}
              onChange={(e) => setDevQuestion(e.target.value)}
              placeholder="Consulta técnica"
            />
            <button type="submit">Enviar</button>
          </form>
          {devAnswer && <p className="bot-reply">{devAnswer}</p>}
        </div>
      </section>

      {errorMessage && (
        <div className="toast toast-error">
          {errorMessage}
        </div>
      )}
    </div>
  )
}

export default ChatWorkspace

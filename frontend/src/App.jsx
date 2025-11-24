import { useState } from 'react'
import './App.css'
import Users from './components/Users'
import Channels from './components/Channels'
import Messages from './components/Messages'
import Files from './components/Files'
import Search from './components/Search'

function App() {
  const [activeView, setActiveView] = useState('users')

  const renderView = () => {
    switch (activeView) {
      case 'users':
        return <Users />
      case 'channels':
        return <Channels />
      case 'messages':
        return <Messages />
      case 'files':
        return <Files />
      case 'search':
        return <Search />
      default:
        return <Users />
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Chat Universitario</h1>
        <nav className="nav">
          <button 
            className={activeView === 'users' ? 'active' : ''} 
            onClick={() => setActiveView('users')}
          >
            Usuarios
          </button>
          <button 
            className={activeView === 'channels' ? 'active' : ''} 
            onClick={() => setActiveView('channels')}
          >
            Canales
          </button>
          <button 
            className={activeView === 'messages' ? 'active' : ''} 
            onClick={() => setActiveView('messages')}
          >
            Mensajes
          </button>
          <button 
            className={activeView === 'files' ? 'active' : ''} 
            onClick={() => setActiveView('files')}
          >
            Archivos
          </button>
          <button 
            className={activeView === 'search' ? 'active' : ''} 
            onClick={() => setActiveView('search')}
          >
            Búsqueda
          </button>
        </nav>
      </header>
      <main className="container">
        {renderView()}
      </main>
    </div>
  )
}

export default App

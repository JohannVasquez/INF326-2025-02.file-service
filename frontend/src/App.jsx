import './App.css'
import ChatWorkspace from './components/ChatWorkspace'

function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <path d="M16 4C9.373 4 4 9.373 4 16c0 2.404.708 4.642 1.927 6.52L4.5 28l5.8-1.52A11.937 11.937 0 0016 28c6.627 0 12-5.373 12-12S22.627 4 16 4z" fill="currentColor"/>
              <path d="M12.5 13.5h7M12.5 17.5h7" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <h1>Chat Universitario Grupo 7</h1>
          </div>
          <div className="header-status">
            <span className="status-dot"></span>
            <span>Conectado</span>
          </div>
        </div>
      </header>
      <main className="main-content">
        <ChatWorkspace />
      </main>
    </div>
  )
}

export default App

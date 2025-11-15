// Estado de la aplicación
const state = {
    user: null,
    token: null,
    currentChannel: null,
    currentThread: null,
    channels: [],
    threads: [],
    messages: [],
    currentChatbot: null
};

// API Base URL
const API_BASE = '/api';

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    loadUserFromStorage();
    loadChannels();
    updateUI();
});

// Utilidades
function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    console.log('Success:', message);
}

function getAuthHeaders() {
    return state.token ? { 'Authorization': `Bearer ${state.token}` } : {};
}

// Gestión de usuario
function loadUserFromStorage() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    if (token && user) {
        state.token = token;
        state.user = JSON.parse(user);
        updateUI();
    }
}

function saveUserToStorage() {
    if (state.token && state.user) {
        localStorage.setItem('token', state.token);
        localStorage.setItem('user', JSON.stringify(state.user));
    }
}

function logout() {
    state.user = null;
    state.token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    updateUI();
}

function updateUI() {
    const userInfo = document.getElementById('userInfo');
    const username = document.getElementById('username');
    const loginBtn = document.querySelector('.top-bar-actions .btn-primary');
    
    if (state.user) {
        username.textContent = state.user.username || state.user.email;
        loginBtn.textContent = 'Cerrar Sesión';
        loginBtn.onclick = logout;
    } else {
        username.textContent = 'Guest';
        loginBtn.textContent = 'Iniciar Sesión';
        loginBtn.onclick = showLoginModal;
    }
}

// Modales
function showModal(modalId) {
    document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

function showLoginModal() {
    closeModal('registerModal');
    showModal('loginModal');
}

function showRegisterModal() {
    closeModal('loginModal');
    showModal('registerModal');
}

function showCreateChannelModal() {
    if (!state.user) {
        showError('Debes iniciar sesión para crear un canal');
        return;
    }
    showModal('createChannelModal');
}

function showCreateThreadModal() {
    if (!state.user) {
        showError('Debes iniciar sesión para crear un hilo');
        return;
    }
    if (!state.currentChannel) {
        showError('Selecciona un canal primero');
        return;
    }
    showModal('createThreadModal');
}

function showSearch() {
    showModal('searchModal');
}

function showSettings() {
    alert('Configuración próximamente');
}

// Autenticación
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/users/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) throw new Error('Login failed');
        
        const data = await response.json();
        state.token = data.access_token || data.token;
        state.user = data.user || { email };
        
        saveUserToStorage();
        closeModal('loginModal');
        updateUI();
        showSuccess('Sesión iniciada correctamente');
    } catch (error) {
        showError('Error al iniciar sesión: ' + error.message);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const fullName = document.getElementById('registerFullName').value;
    
    try {
        const response = await fetch(`${API_BASE}/users/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, full_name: fullName })
        });
        
        if (!response.ok) throw new Error('Registration failed');
        
        const data = await response.json();
        closeModal('registerModal');
        showSuccess('Registro exitoso. Por favor inicia sesión.');
        showLoginModal();
    } catch (error) {
        showError('Error al registrar: ' + error.message);
    }
}

// Canales
async function loadChannels() {
    try {
        const response = await fetch(`${API_BASE}/channels`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to load channels');
        
        state.channels = await response.json();
        renderChannels();
    } catch (error) {
        console.error('Error loading channels:', error);
        // Mostrar canales de ejemplo si falla
        state.channels = [
            { id: 1, name: 'General', subject: 'General' },
            { id: 2, name: 'Matemáticas', subject: 'Matemáticas' },
            { id: 3, name: 'Programación', subject: 'Programación' }
        ];
        renderChannels();
    }
}

function renderChannels() {
    const channelsList = document.getElementById('channelsList');
    channelsList.innerHTML = '';
    
    state.channels.forEach(channel => {
        const channelItem = document.createElement('div');
        channelItem.className = 'channel-item';
        if (state.currentChannel?.id === channel.id) {
            channelItem.classList.add('active');
        }
        
        channelItem.innerHTML = `
            <span class="channel-icon">#</span>
            <span class="channel-name">${channel.name}</span>
        `;
        
        channelItem.onclick = () => selectChannel(channel);
        channelsList.appendChild(channelItem);
    });
}

async function selectChannel(channel) {
    state.currentChannel = channel;
    state.currentThread = null;
    
    document.getElementById('channelName').textContent = channel.name;
    document.getElementById('channelDescription').textContent = channel.subject || '';
    
    renderChannels();
    await loadThreads();
    
    document.getElementById('threadsContainer').style.display = 'block';
    document.getElementById('messagesArea').style.display = 'none';
}

async function handleCreateChannel(event) {
    event.preventDefault();
    const name = document.getElementById('channelName').value;
    const description = document.getElementById('channelDescription').value;
    const subject = document.getElementById('channelSubject').value;
    const isPrivate = document.getElementById('channelPrivate').checked;
    
    try {
        const response = await fetch(`${API_BASE}/channels`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({ name, description, subject, is_private: isPrivate })
        });
        
        if (!response.ok) throw new Error('Failed to create channel');
        
        const newChannel = await response.json();
        state.channels.push(newChannel);
        renderChannels();
        closeModal('createChannelModal');
        showSuccess('Canal creado correctamente');
    } catch (error) {
        showError('Error al crear canal: ' + error.message);
    }
}

// Hilos
async function loadThreads() {
    if (!state.currentChannel) return;
    
    try {
        const response = await fetch(`${API_BASE}/threads?channel_id=${state.currentChannel.id}`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to load threads');
        
        state.threads = await response.json();
        renderThreads();
    } catch (error) {
        console.error('Error loading threads:', error);
        state.threads = [];
        renderThreads();
    }
}

function renderThreads() {
    const threadsList = document.getElementById('threadsList');
    threadsList.innerHTML = '';
    
    if (state.threads.length === 0) {
        threadsList.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">No hay hilos en este canal. ¡Crea el primero!</p>';
        return;
    }
    
    state.threads.forEach(thread => {
        const threadItem = document.createElement('div');
        threadItem.className = 'thread-item';
        
        threadItem.innerHTML = `
            <div class="thread-header">
                <div class="thread-title">${thread.title}</div>
                <div class="thread-meta">${thread.created_at ? new Date(thread.created_at).toLocaleDateString() : 'Reciente'}</div>
            </div>
            <div class="thread-preview">${thread.content || 'Sin contenido'}</div>
            <div class="thread-stats">
                <span>💬 ${thread.message_count || 0} mensajes</span>
                <span>👤 ${thread.author || 'Anónimo'}</span>
            </div>
        `;
        
        threadItem.onclick = () => selectThread(thread);
        threadsList.appendChild(threadItem);
    });
}

async function selectThread(thread) {
    state.currentThread = thread;
    
    document.getElementById('threadTitle').textContent = thread.title;
    document.getElementById('threadInfo').textContent = `Por ${thread.author || 'Anónimo'}`;
    
    document.getElementById('threadsContainer').style.display = 'none';
    document.getElementById('messagesArea').style.display = 'flex';
    
    await loadMessages();
}

function backToThreads() {
    state.currentThread = null;
    document.getElementById('threadsContainer').style.display = 'block';
    document.getElementById('messagesArea').style.display = 'none';
}

async function handleCreateThread(event) {
    event.preventDefault();
    const title = document.getElementById('threadTitle').value;
    const content = document.getElementById('threadContent').value;
    
    try {
        const response = await fetch(`${API_BASE}/threads`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({ 
                title, 
                content,
                channel_id: state.currentChannel.id 
            })
        });
        
        if (!response.ok) throw new Error('Failed to create thread');
        
        const newThread = await response.json();
        state.threads.unshift(newThread);
        renderThreads();
        closeModal('createThreadModal');
        showSuccess('Hilo creado correctamente');
    } catch (error) {
        showError('Error al crear hilo: ' + error.message);
    }
}

// Mensajes
async function loadMessages() {
    if (!state.currentThread) return;
    
    try {
        const response = await fetch(`${API_BASE}/messages?thread_id=${state.currentThread.id}`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to load messages');
        
        state.messages = await response.json();
        renderMessages();
    } catch (error) {
        console.error('Error loading messages:', error);
        state.messages = [];
        renderMessages();
    }
}

function renderMessages() {
    const messagesContainer = document.getElementById('messagesContainer');
    messagesContainer.innerHTML = '';
    
    if (state.messages.length === 0) {
        messagesContainer.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No hay mensajes. ¡Sé el primero en escribir!</p>';
        return;
    }
    
    state.messages.forEach(message => {
        const messageItem = document.createElement('div');
        messageItem.className = 'message-item';
        
        const authorInitial = (message.author || 'U')[0].toUpperCase();
        const timestamp = message.created_at ? new Date(message.created_at).toLocaleString() : 'Ahora';
        
        messageItem.innerHTML = `
            <div class="message-avatar">${authorInitial}</div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-author">${message.author || 'Usuario'}</span>
                    <span class="message-timestamp">${timestamp}</span>
                </div>
                <div class="message-text">${message.content}</div>
                ${message.attachments ? renderAttachments(message.attachments) : ''}
                ${message.reactions ? renderReactions(message.reactions) : ''}
            </div>
        `;
        
        messagesContainer.appendChild(messageItem);
    });
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function renderAttachments(attachments) {
    if (!attachments || attachments.length === 0) return '';
    
    return `
        <div class="message-attachments">
            ${attachments.map(att => `
                <a href="${att.url}" class="attachment-item" target="_blank">
                    📎 ${att.filename}
                </a>
            `).join('')}
        </div>
    `;
}

function renderReactions(reactions) {
    if (!reactions || reactions.length === 0) return '';
    
    return `
        <div class="message-reactions">
            ${reactions.map(reaction => `
                <button class="reaction-btn">${reaction.emoji} ${reaction.count}</button>
            `).join('')}
        </div>
    `;
}

async function sendMessage() {
    if (!state.user) {
        showError('Debes iniciar sesión para enviar mensajes');
        return;
    }
    
    if (!state.currentThread) {
        showError('Selecciona un hilo primero');
        return;
    }
    
    const input = document.getElementById('messageInput');
    const content = input.value.trim();
    
    if (!content) return;
    
    try {
        const response = await fetch(`${API_BASE}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({
                content,
                thread_id: state.currentThread.id,
                author: state.user.username || state.user.email
            })
        });
        
        if (!response.ok) throw new Error('Failed to send message');
        
        const newMessage = await response.json();
        state.messages.push(newMessage);
        renderMessages();
        input.value = '';
    } catch (error) {
        showError('Error al enviar mensaje: ' + error.message);
    }
}

function handleMessageKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Archivos
async function showFileUpload() {
    if (!state.user) {
        showError('Debes iniciar sesión para subir archivos');
        return;
    }
    
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    
    input.onchange = async (e) => {
        const files = e.target.files;
        if (files.length === 0) return;
        
        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }
        
        try {
            const response = await fetch(`${API_BASE}/files/upload`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });
            
            if (!response.ok) throw new Error('Failed to upload files');
            
            const uploadedFiles = await response.json();
            showSuccess(`${uploadedFiles.length} archivo(s) subido(s) correctamente`);
            
            // Añadir referencia al mensaje actual si está en un hilo
            if (state.currentThread) {
                const messageInput = document.getElementById('messageInput');
                const fileLinks = uploadedFiles.map(f => `📎 ${f.filename}`).join(', ');
                messageInput.value += `\n${fileLinks}`;
            }
        } catch (error) {
            showError('Error al subir archivos: ' + error.message);
        }
    };
    
    input.click();
}

// Chatbots
function openChatbot(type) {
    state.currentChatbot = type;
    
    const titles = {
        academic: '📖 Chatbot Académico',
        utility: '⚡ Chatbot de Utilidades',
        calc: '🔢 Calculadora',
        wiki: '📰 Wikipedia Bot',
        programming: '💻 Asistente de Programación'
    };
    
    document.getElementById('chatbotTitle').textContent = titles[type] || 'Chatbot';
    document.getElementById('chatbotMessages').innerHTML = `
        <div class="chatbot-message bot">
            ¡Hola! Soy el ${titles[type]}. ¿En qué puedo ayudarte?
        </div>
    `;
    
    showModal('chatbotModal');
}

async function sendChatbotMessage() {
    const input = document.getElementById('chatbotInput');
    const question = input.value.trim();
    
    if (!question) return;
    
    const messagesContainer = document.getElementById('chatbotMessages');
    
    // Añadir mensaje del usuario
    const userMessage = document.createElement('div');
    userMessage.className = 'chatbot-message user';
    userMessage.textContent = question;
    messagesContainer.appendChild(userMessage);
    
    input.value = '';
    
    // Enviar a la API del chatbot
    try {
        const endpoints = {
            academic: '/chatbot/academic',
            utility: '/chatbot/utility',
            calc: '/chatbot/calc',
            wiki: '/chatbot/wiki',
            programming: '/chatbot/programming'
        };
        
        const response = await fetch(`${API_BASE}${endpoints[state.currentChatbot]}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) throw new Error('Chatbot request failed');
        
        const data = await response.json();
        const botMessage = document.createElement('div');
        botMessage.className = 'chatbot-message bot';
        botMessage.textContent = data.response || data.answer || 'Lo siento, no pude procesar tu pregunta.';
        messagesContainer.appendChild(botMessage);
    } catch (error) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'chatbot-message bot';
        errorMessage.textContent = 'Lo siento, ocurrió un error al procesar tu pregunta.';
        messagesContainer.appendChild(errorMessage);
    }
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function handleChatbotKeydown(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendChatbotMessage();
    }
}

// Búsqueda
let searchTimeout;
async function handleSearch() {
    clearTimeout(searchTimeout);
    
    const input = document.getElementById('searchInput');
    const query = input.value.trim();
    
    if (query.length < 2) {
        document.getElementById('searchResults').innerHTML = '';
        return;
    }
    
    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`, {
                headers: getAuthHeaders()
            });
            
            if (!response.ok) throw new Error('Search failed');
            
            const results = await response.json();
            renderSearchResults(results);
        } catch (error) {
            console.error('Search error:', error);
            document.getElementById('searchResults').innerHTML = '<p style="color: var(--text-muted);">No se encontraron resultados</p>';
        }
    }, 300);
}

function renderSearchResults(results) {
    const container = document.getElementById('searchResults');
    container.innerHTML = '';
    
    if (!results || results.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">No se encontraron resultados</p>';
        return;
    }
    
    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        
        item.innerHTML = `
            <div class="search-result-type">${result.type || 'Mensaje'}</div>
            <div class="search-result-title">${result.title || 'Sin título'}</div>
            <div class="search-result-content">${result.content || ''}</div>
        `;
        
        item.onclick = () => {
            closeModal('searchModal');
            // Navegar al resultado
        };
        
        container.appendChild(item);
    });
}

// Configuración de la API Gateway
const API_BASE_URL = 'http://localhost:8000/api';

// Estado de la aplicación
let currentFiles = [];

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Aplicación iniciada');
    checkHealth();
    setupFileInput();
    
    // Cargar archivos automáticamente
    if (document.getElementById('listTab').classList.contains('active')) {
        loadFiles();
    }
});

// ==================== HEALTH CHECK ====================
async function checkHealth() {
    try {
        const response = await fetch('http://localhost:8000/health/services');
        const data = await response.json();
        
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (data.gateway === 'up' && data.services.files.status === 'up') {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Servicios en línea';
        } else {
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Algunos servicios offline';
        }
        
        // Actualizar estado de servicios en About tab
        updateServicesStatus(data);
    } catch (error) {
        console.error('Error checking health:', error);
        document.getElementById('statusDot').className = 'status-dot offline';
        document.getElementById('statusText').textContent = 'Error de conexión';
    }
}

function updateServicesStatus(data) {
    const container = document.getElementById('servicesStatus');
    if (!container) return;
    
    const html = `
        <div class="service-item ${data.gateway === 'up' ? 'online' : 'offline'}">
            <strong>API Gateway:</strong> ${data.gateway}
        </div>
        <div class="service-item ${data.services.files?.status === 'up' ? 'online' : 'offline'}">
            <strong>Servicio de Archivos:</strong> ${data.services.files?.status || 'unknown'}
            <br><small>${data.services.files?.url || ''}</small>
        </div>
    `;
    
    container.innerHTML = html;
}

// ==================== NAVEGACIÓN DE TABS ====================
function showTab(tabName) {
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Desactivar todos los botones
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Mostrar tab seleccionado
    const tabId = tabName + 'Tab';
    document.getElementById(tabId).classList.add('active');
    
    // Activar botón correspondiente
    event.target.classList.add('active');
    
    // Cargar datos si es necesario
    if (tabName === 'list') {
        loadFiles();
    } else if (tabName === 'about') {
        checkHealth();
    }
}

// ==================== FILE INPUT ====================
function setupFileInput() {
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileName.textContent = e.target.files[0].name;
        } else {
            fileName.textContent = 'Ningún archivo seleccionado';
        }
    });
}

// ==================== UPLOAD FILE ====================
async function uploadFile(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    const uploadBtn = document.getElementById('uploadBtnText');
    const spinner = document.getElementById('uploadSpinner');
    const resultDiv = document.getElementById('uploadResult');
    
    // Mostrar spinner
    uploadBtn.style.display = 'none';
    spinner.style.display = 'inline-block';
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/files/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showResult(resultDiv, 'success', `
                ✅ Archivo subido exitosamente
                <br><small>ID: ${data.id}</small>
                <br><small>Tamaño: ${formatBytes(data.size)}</small>
            `);
            
            // Limpiar formulario
            form.reset();
            document.getElementById('fileName').textContent = 'Ningún archivo seleccionado';
            
            // Actualizar lista si está visible
            if (document.getElementById('listTab').classList.contains('active')) {
                loadFiles();
            }
        } else {
            throw new Error(data.detail || 'Error al subir archivo');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showResult(resultDiv, 'error', `❌ Error: ${error.message}`);
    } finally {
        uploadBtn.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// ==================== LOAD FILES ====================
async function loadFiles() {
    const container = document.getElementById('filesList');
    const messageId = document.getElementById('filterMessageId')?.value;
    const threadId = document.getElementById('filterThreadId')?.value;
    
    container.innerHTML = '<p class="loading">Cargando archivos...</p>';
    
    try {
        let url = `${API_BASE_URL}/files?limit=50&offset=0`;
        if (messageId) url += `&message_id=${messageId}`;
        if (threadId) url += `&thread_id=${threadId}`;
        
        const response = await fetch(url);
        const files = await response.json();
        
        if (response.ok) {
            currentFiles = Array.isArray(files) ? files : [];
            displayFiles(currentFiles);
        } else {
            throw new Error('Error al cargar archivos');
        }
    } catch (error) {
        console.error('Load files error:', error);
        container.innerHTML = `<p class="error">❌ Error al cargar archivos: ${error.message}</p>`;
    }
}

function displayFiles(files) {
    const container = document.getElementById('filesList');
    
    if (!files || files.length === 0) {
        container.innerHTML = '<p class="empty-state">📂 No hay archivos para mostrar</p>';
        return;
    }
    
    const html = files.map(file => `
        <div class="file-card">
            <div class="file-icon">${getFileIcon(file.mime_type)}</div>
            <div class="file-info">
                <div class="file-name">${file.filename}</div>
                <div class="file-meta">
                    <span>📊 ${formatBytes(file.size)}</span>
                    <span>📅 ${formatDate(file.created_at)}</span>
                    ${file.message_id ? `<span>💬 Msg: ${file.message_id.substring(0, 8)}...</span>` : ''}
                    ${file.thread_id ? `<span>🧵 Thread: ${file.thread_id.substring(0, 8)}...</span>` : ''}
                </div>
                <div class="file-type">${file.mime_type}</div>
            </div>
            <div class="file-actions">
                <button onclick="downloadFile('${file.id}')" class="btn-icon" title="Descargar">
                    ⬇️
                </button>
                <button onclick="viewFileDetails('${file.id}')" class="btn-icon" title="Ver detalles">
                    👁️
                </button>
                <button onclick="deleteFile('${file.id}')" class="btn-icon btn-danger" title="Eliminar">
                    🗑️
                </button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// ==================== SEARCH FILE ====================
async function searchFile(event) {
    event.preventDefault();
    
    const fileId = document.getElementById('searchFileId').value;
    const resultDiv = document.getElementById('searchResult');
    
    resultDiv.innerHTML = '<p class="loading">Buscando...</p>';
    resultDiv.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/files/${fileId}`);
        const file = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="file-details">
                    <h3>📄 ${file.filename}</h3>
                    <div class="detail-row"><strong>ID:</strong> ${file.id}</div>
                    <div class="detail-row"><strong>Tamaño:</strong> ${formatBytes(file.size)}</div>
                    <div class="detail-row"><strong>Tipo:</strong> ${file.mime_type}</div>
                    <div class="detail-row"><strong>Bucket:</strong> ${file.bucket}</div>
                    <div class="detail-row"><strong>Object Key:</strong> ${file.object_key}</div>
                    <div class="detail-row"><strong>Creado:</strong> ${formatDate(file.created_at)}</div>
                    ${file.message_id ? `<div class="detail-row"><strong>Mensaje ID:</strong> ${file.message_id}</div>` : ''}
                    ${file.thread_id ? `<div class="detail-row"><strong>Hilo ID:</strong> ${file.thread_id}</div>` : ''}
                    <div class="detail-row"><strong>Checksum:</strong> <code>${file.checksum_sha256}</code></div>
                    
                    <div class="detail-actions">
                        <button onclick="downloadFile('${file.id}')" class="btn btn-primary">⬇️ Descargar</button>
                        <button onclick="deleteFile('${file.id}')" class="btn btn-danger">🗑️ Eliminar</button>
                    </div>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `<p class="error">❌ Archivo no encontrado</p>`;
        }
    } catch (error) {
        console.error('Search error:', error);
        resultDiv.innerHTML = `<p class="error">❌ Error: ${error.message}</p>`;
    }
}

// ==================== FILE ACTIONS ====================
async function downloadFile(fileId) {
    try {
        const response = await fetch(`${API_BASE_URL}/files/${fileId}/download-url`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok && data.download_url) {
            window.open(data.download_url, '_blank');
        } else {
            alert('Error obteniendo URL de descarga');
        }
    } catch (error) {
        console.error('Download error:', error);
        alert('Error al descargar archivo');
    }
}

async function deleteFile(fileId) {
    if (!confirm('¿Estás seguro de que deseas eliminar este archivo?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
            method: 'DELETE'
        });
        
        if (response.ok || response.status === 204) {
            alert('✅ Archivo eliminado exitosamente');
            loadFiles(); // Recargar lista
        } else {
            throw new Error('Error al eliminar archivo');
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('❌ Error al eliminar archivo');
    }
}

function viewFileDetails(fileId) {
    // Cambiar a tab de búsqueda y mostrar detalles
    showTab('search');
    document.getElementById('searchFileId').value = fileId;
    document.getElementById('searchFileId').form.dispatchEvent(new Event('submit'));
}

// ==================== UTILIDADES ====================
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-CL');
}

function getFileIcon(mimeType) {
    if (!mimeType) return '📄';
    if (mimeType.startsWith('image/')) return '🖼️';
    if (mimeType.startsWith('video/')) return '🎥';
    if (mimeType.startsWith('audio/')) return '🎵';
    if (mimeType.includes('pdf')) return '📕';
    if (mimeType.includes('word')) return '📘';
    if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return '📊';
    if (mimeType.includes('zip') || mimeType.includes('rar')) return '📦';
    return '📄';
}

function showResult(element, type, message) {
    element.className = `result-message ${type}`;
    element.innerHTML = message;
    element.style.display = 'block';
    
    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

# 🌐 Frontend - Sistema de Gestión de Archivos

Interfaz web moderna para interactuar con el sistema de gestión de archivos.

## 🚀 Ejecutar

### Opción 1: Servidor Python Simple
```bash
cd frontend
python -m http.server 8080
```

### Opción 2: Live Server (VS Code)
1. Instala la extensión "Live Server" en VS Code
2. Click derecho en `index.html` → "Open with Live Server"

### Opción 3: Cualquier servidor web
```bash
# Node.js
npx serve frontend

# PHP
php -S localhost:8080 -t frontend
```

Abrir: http://localhost:8080

## ✨ Características

### 📤 Subir Archivos
- Drag & drop de archivos
- Asociar a mensajes o hilos
- Feedback visual del proceso

### 📋 Listar Archivos
- Vista de todos los archivos
- Filtros por mensaje o hilo
- Información detallada de cada archivo

### 🔍 Buscar
- Búsqueda por ID de archivo
- Vista detallada con todos los metadatos

### ℹ️ Información
- Estado de los servicios
- Información del equipo
- Enlaces a documentación

## 🎨 Tecnologías

- **HTML5** - Estructura semántica
- **CSS3** - Diseño moderno y responsive
- **JavaScript (Vanilla)** - Sin frameworks, ligero y rápido
- **Fetch API** - Comunicación con el backend

## 🔧 Configuración

El frontend se conecta al API Gateway en:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

Para cambiar la URL, edita `app.js` línea 2.

## 📱 Responsive

La interfaz está optimizada para:
- 💻 Desktop
- 📱 Tablets
- 📱 Móviles

## 🎯 Estructura de Archivos

```
frontend/
├── index.html      # Página principal
├── app.js          # Lógica de la aplicación
├── styles.css      # Estilos
└── README.md       # Esta documentación
```

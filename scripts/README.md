# 🛠️ Scripts de Automatización

Esta carpeta contiene scripts PowerShell para automatizar tareas de Kubernetes.

## 📜 Scripts Disponibles

### 🚀 `guided-deploy.ps1` - **RECOMENDADO PARA PRINCIPIANTES**
Asistente interactivo que te guía paso a paso en todo el proceso de despliegue.

```powershell
.\scripts\guided-deploy.ps1
```

**Incluye:**
- Verificación de prerrequisitos
- Configuración de kubectl
- Configuración de Docker Hub
- Build y push de imagen
- Despliegue completo
- Verificación post-despliegue
- Setup de CI/CD

---

### 🔍 `preflight-check.ps1` - Verificación Pre-vuelo
Verifica que todo esté configurado correctamente antes de desplegar.

```powershell
.\scripts\preflight-check.ps1
```

**Verifica:**
- kubectl instalado y funcionando
- Conexión al cluster
- Docker disponible
- Manifiestos de K8s presentes
- Ingress Controller
- Metrics Server

---

### 🚀 `deploy.ps1` - Despliegue Automatizado
Despliega toda la aplicación al cluster en orden correcto.

```powershell
# Despliegue completo
.\scripts\deploy.ps1

# Saltar dependencias (si ya están desplegadas)
.\scripts\deploy.ps1 -SkipDependencies

# Ver logs después del despliegue
.\scripts\deploy.ps1 -WatchLogs
```

**Despliega:**
1. Namespace
2. ConfigMap y Secrets
3. PostgreSQL
4. MinIO
5. RabbitMQ
6. Aplicación
7. HPA
8. Ingress

---

### 📊 `status.ps1` - Ver Estado del Cluster
Muestra un resumen completo del estado de todos los recursos.

```powershell
.\scripts\status.ps1
```

**Muestra:**
- Información del cluster
- Estado de los pods
- Servicios
- Deployments
- HPA
- Ingress
- PVCs
- Eventos recientes
- Uso de recursos

---

### 🗑️ `cleanup.ps1` - Limpiar Recursos
Elimina todos los recursos del namespace.

```powershell
# Con confirmación
.\scripts\cleanup.ps1

# Sin confirmación (cuidado!)
.\scripts\cleanup.ps1 -Force
```

⚠️ **ADVERTENCIA**: Esto eliminará todo el namespace y sus recursos.

---

### 🐳 `build-and-push.ps1` - Build y Push Docker
Construye la imagen Docker y la sube a Docker Hub.

```powershell
# Build con tag latest
.\scripts\build-and-push.ps1

# Build con tag específico
.\scripts\build-and-push.ps1 -Tag "v1.0.0"

# Con repositorio personalizado
.\scripts\build-and-push.ps1 -Repository "tu-usuario/file-service" -Tag "latest"
```

**Requisito**: Haber hecho `docker login` primero.

---

### 🔐 `generate-github-secrets.ps1` - Generador de Secrets
Helper interactivo para configurar secrets de GitHub Actions.

```powershell
.\scripts\generate-github-secrets.ps1
```

**Genera:**
- KUBECONFIG en base64
- Guía para DOCKER_USERNAME
- Guía para DOCKER_PASSWORD
- Actualiza archivos automáticamente

---

## 🎯 Flujo de Trabajo Recomendado

### Primera vez (Principiantes):

```powershell
# 1. Ejecutar asistente guiado
.\scripts\guided-deploy.ps1
```

### Primera vez (Avanzados):

```powershell
# 1. Verificar todo
.\scripts\preflight-check.ps1

# 2. Configurar GitHub secrets (si quieres CI/CD)
.\scripts\generate-github-secrets.ps1

# 3. Build y push
.\scripts\build-and-push.ps1

# 4. Desplegar
.\scripts\deploy.ps1

# 5. Verificar
.\scripts\status.ps1
```

### Desarrollo continuo:

```powershell
# Hacer cambios en el código...

# Build y push nueva versión
.\scripts\build-and-push.ps1

# Reiniciar deployment
kubectl rollout restart deployment/file-service-api -n file-service

# Ver logs
kubectl logs -l app=file-service-api -n file-service -f
```

### Troubleshooting:

```powershell
# Ver estado
.\scripts\status.ps1

# Ver logs
kubectl logs -l app=file-service-api -n file-service -f

# Si hay problemas, limpiar y redesplegar
.\scripts\cleanup.ps1
.\scripts\deploy.ps1
```

---

## 💡 Tips

### Variables de entorno
Los scripts usan estas variables importantes:

```powershell
# Configurar KUBECONFIG
$env:KUBECONFIG="c:\Users\pipe2\OneDrive\Documentos\GitHub\INF326-2025-02.file-service\k8s-inf326-nyc1-kubeconfig.yaml"
```

### Permisos de ejecución
Si PowerShell bloquea los scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Namespace por defecto
Todos los scripts usan el namespace `file-service`.

---

## 🔧 Personalización

Puedes modificar los scripts según tus necesidades. Variables comunes:

- `$namespace = "file-service"` - Nombre del namespace
- `$DOCKER_IMAGE` - Repositorio de Docker
- Timeouts de espera
- Nombres de archivos de manifiestos

---

## 📚 Documentación Relacionada

- [KUBERNETES.md](../KUBERNETES.md) - Documentación completa de K8s
- [QUICKSTART_K8S.md](../QUICKSTART_K8S.md) - Guía paso a paso
- [CHECKLIST.md](../CHECKLIST.md) - Lista de verificación
- [GITHUB_SECRETS.md](../GITHUB_SECRETS.md) - Configuración de CI/CD

---

## 🆘 Problemas Comunes

### "No se reconoce como comando"
Ejecuta desde la raíz del proyecto:
```powershell
cd c:\Users\pipe2\OneDrive\Documentos\GitHub\INF326-2025-02.file-service
.\scripts\nombre-script.ps1
```

### "Cannot connect to cluster"
Configura KUBECONFIG:
```powershell
$env:KUBECONFIG="c:\Users\pipe2\OneDrive\Documentos\GitHub\INF326-2025-02.file-service\k8s-inf326-nyc1-kubeconfig.yaml"
```

### Scripts bloqueados
Habilita ejecución:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🎓 Para Estudiantes

Si eres nuevo en Kubernetes:
1. ✅ Empieza con `guided-deploy.ps1`
2. ✅ Lee `QUICKSTART_K8S.md`
3. ✅ Usa `k9s` para ver todo visualmente
4. ✅ Experimenta con los comandos
5. ✅ Lee la documentación completa

---

¡Happy Deploying! 🚀

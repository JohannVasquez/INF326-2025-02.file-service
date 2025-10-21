from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import files as files_router
from .storage import ensure_bucket
from .events import event_bus

app = FastAPI(
    title="Servicio de Archivos",
    version="1.0.0",
    default_response_class=JSONResponse
)

# CORS (ajusta dominios en prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    ensure_bucket()
    await event_bus.connect()

@app.get("/healthz")
async def healthz():
    return {"status":"ok","service": settings.app_name, "env": settings.app_env}

# Error handler uniforme
@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    # En producción loggea con stacktrace
    return JSONResponse(status_code=500, content={"error":{"code":"INTERNAL_ERROR","message": str(exc), "details": None}})

# Routers
app.include_router(files_router.router)

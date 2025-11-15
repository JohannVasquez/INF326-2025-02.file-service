FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/
COPY static/ ./static/
COPY run.py .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["python", "run.py"]

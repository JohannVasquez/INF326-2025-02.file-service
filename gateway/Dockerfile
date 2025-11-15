FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del gateway
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando para correr el gateway
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

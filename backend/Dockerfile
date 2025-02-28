FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema incluindo compilador C
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libc-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

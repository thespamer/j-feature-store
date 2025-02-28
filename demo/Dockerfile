FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY demo/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Criar diretórios necessários
RUN mkdir -p /app/data/transformations /app/data/pipelines /app/transformations /app/pipelines

# Copiar arquivos de demonstração
COPY demo/transformations /app/transformations/
COPY demo/pipelines /app/pipelines/
COPY demo/generate_data.py .

# Comando para iniciar o script
CMD ["python", "generate_data.py"]

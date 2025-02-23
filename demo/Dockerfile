FROM python:3.9-slim

WORKDIR /app

# Copiar arquivos necessários
COPY demo/generate_data.py .
COPY demo/requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Definir variáveis de ambiente
ENV MONGODB_URI=mongodb://mongodb:27017/fstore
ENV REDIS_URI=redis://redis:6379/0

# Comando para executar a geração de dados
CMD ["python3", "generate_data.py"]

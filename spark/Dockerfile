FROM jupyter/pyspark-notebook:latest

WORKDIR /app

USER root

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Baixar driver JDBC do PostgreSQL
RUN wget https://jdbc.postgresql.org/download/postgresql-42.2.18.jar -O /app/postgresql-42.2.18.jar

# Copiar requirements.txt e instalar dependências Python
COPY spark/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY spark/feature_processor /app/feature_processor

# Set environment variables
ENV SPARK_MASTER_URL=local[*]
ENV SPARK_DRIVER_MEMORY=4g
ENV SPARK_EXECUTOR_MEMORY=4g

# Expose Spark UI port
EXPOSE 4040

# Comando para iniciar o processador
CMD ["python", "-m", "feature_processor.processor"]

FROM jupyter/pyspark-notebook:latest

WORKDIR /app

USER root

# Download PostgreSQL JDBC driver
RUN wget https://jdbc.postgresql.org/download/postgresql-42.2.18.jar -O /app/postgresql-42.2.18.jar

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY feature_processor.py .

# Set environment variables
ENV SPARK_MASTER_URL=local[*]
ENV SPARK_DRIVER_MEMORY=4g
ENV SPARK_EXECUTOR_MEMORY=4g

# Expose Spark UI port
EXPOSE 4040

CMD ["python", "feature_processor.py"]

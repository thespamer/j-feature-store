FROM apache/spark-py:3.4.0

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Spark application files
COPY feature_processor.py .

# Set environment variables
ENV SPARK_MASTER_URL=local[*]
ENV SPARK_DRIVER_MEMORY=4g
ENV SPARK_EXECUTOR_MEMORY=4g

# Expose Spark UI port
EXPOSE 4040

CMD ["python", "feature_processor.py"]

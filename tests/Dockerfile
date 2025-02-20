FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY e2e_test.py .
COPY wait-for-it.sh .
RUN chmod +x wait-for-it.sh

CMD ["./wait-for-it.sh", "backend", "8000", "./wait-for-it.sh", "kafka", "9092", "./wait-for-it.sh", "postgres", "5432", "python", "e2e_test.py"]

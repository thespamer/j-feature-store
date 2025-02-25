# Quick Start Guide

## Prerequisites
- Docker and Docker Compose
- Python 3.8 or higher
- curl (for API examples)

## Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/feature-store.git
cd feature-store
```

2. **Start the Services**
```bash
docker compose up -d
```

This will start:
- Backend API (FastAPI)
- Feature Processor (Spark)
- PostgreSQL
- MongoDB
- Redis
- Kafka & Zookeeper

3. **Verify Services**
```bash
# Check health endpoint
curl http://localhost:8000/api/v1/monitoring/health

# Check metrics
curl http://localhost:8000/api/v1/monitoring/metrics
```

## Basic Usage

### 1. Create a Feature Group
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "name": "user_features",
    "description": "User behavioral features",
    "entity_id": "user_id",
    "entity_type": "user"
  }' \
  http://localhost:8000/api/v1/feature-groups/
```

### 2. Create a Feature
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "name": "purchase_count",
    "description": "Number of purchases",
    "feature_group_id": "<feature_group_id>",
    "type": "double",
    "entity_id": "user_id"
  }' \
  http://localhost:8000/api/v1/features/
```

### 3. Store a Feature Value
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "feature_id": "<feature_id>",
    "entity_id": "user123",
    "value": 42.0,
    "timestamp": "2025-02-25T11:17:00Z"
  }' \
  http://localhost:8000/api/v1/features/<feature_id>/values
```

### 4. Retrieve a Feature Value
```bash
curl http://localhost:8000/api/v1/features/<feature_id>/values/user123
```

## Environment Variables

The system can be configured using these environment variables:

```bash
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=fstore
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# MongoDB
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DB=fstore

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC=feature_events
```

## Development Setup

1. **Install Dependencies**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Feature Processor
cd spark
pip install -r requirements.txt
```

2. **Run Tests**
```bash
# Unit tests
pytest backend/tests/unit

# Integration tests
pytest backend/tests/integration

# End-to-end tests
pytest e2e/tests
```

3. **Local Development**
```bash
# Start backend in development mode
cd backend
uvicorn app.main:app --reload

# Start feature processor
cd spark
python -m feature_processor.processor
```

## Common Issues

1. **Service Dependencies**
- Ensure PostgreSQL is fully initialized before starting the backend
- Wait for Kafka to be ready before starting the feature processor
- Check service health endpoints if experiencing connection issues

2. **Data Types**
- Feature values must match their defined types
- Timestamps should be in ISO format
- IDs should be valid strings

3. **Performance**
- Use batch operations for multiple feature values
- Monitor Redis cache hit rates
- Check Kafka consumer lag

## Next Steps

1. **Production Deployment**
- Set up monitoring and alerting
- Configure backup and recovery
- Implement authentication and authorization

2. **Feature Development**
- Add new feature types
- Implement feature versioning
- Add batch import/export capabilities

3. **Integration**
- Connect with ML training pipelines
- Set up real-time feature generation
- Implement feature serving API

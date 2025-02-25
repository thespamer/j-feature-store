# Testing Guide

This document describes how to run and write tests for the Feature Store project.

## Test Environment Setup

The project uses Docker Compose to create an isolated test environment with all necessary dependencies:

- MongoDB for feature storage
- Redis for caching
- Kafka for event streaming
- PostgreSQL for metadata storage

## Running Tests

To run all tests, execute:

```bash
docker compose build backend-test
docker compose run --rm backend-test
```

This will:
1. Build the test container with all required dependencies
2. Run the test suite in an isolated environment
3. Display test results with detailed output

## Test Structure

### Directory Structure

```
backend/
├── tests/
│   ├── conftest.py         # Test configuration and fixtures
│   ├── test_monitoring.py  # Tests for monitoring endpoints
│   └── ...                 # Other test files
```

### Test Configuration

The test environment is configured in `backend/tests/conftest.py` with:
- Event loop setup for async tests
- Feature store initialization
- Database connections setup

### Available Test Suites

#### Monitoring Tests (`test_monitoring.py`)

Tests the health and metrics endpoints:

1. Health Check (`test_health_check`):
   - Verifies the `/api/v1/monitoring/health` endpoint
   - Checks MongoDB and Redis connection status
   - Validates response format and status codes

2. Metrics (`test_metrics`):
   - Tests the `/api/v1/monitoring/metrics` endpoint
   - Verifies feature store statistics
   - Validates connection health status

## Writing New Tests

### Test Requirements

Tests should be written using:
- `pytest` for test framework
- `pytest-asyncio` for async test support
- `httpx` for async HTTP client

### Example Test

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_example():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/your-endpoint")
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data
```

### Best Practices

1. Use async/await for all database and HTTP operations
2. Isolate tests using fixtures when needed
3. Clean up any test data after tests complete
4. Use descriptive test names and clear assertions
5. Add proper error messages to assertions

## Environment Variables

The test environment uses these environment variables:

```yaml
MONGODB_URI=mongodb://mongodb:27017/fstore
REDIS_URI=redis://redis:6379/0
POSTGRES_URI=postgresql://postgres:postgres@postgres:5432/fstore
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
TESTING=true
```

## Troubleshooting

Common issues and solutions:

1. **Connection Errors**:
   - Ensure all required services are running (`docker compose ps`)
   - Check service logs (`docker compose logs <service-name>`)

2. **Test Failures**:
   - Verify environment variables are set correctly
   - Check database connectivity
   - Ensure feature store is properly initialized

3. **Import Errors**:
   - Verify PYTHONPATH is set to `/app`
   - Check all dependencies are installed
   - Ensure package structure is correct

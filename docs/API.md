# FStore API Documentation

## Overview

The FStore API provides endpoints for managing features and feature values in the feature store. It uses MongoDB for persistent storage and Redis for caching.

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### Features

#### List Features

```http
GET /features
```

Query Parameters:
- `entity_id` (optional): Filter features by entity ID

Response:
```json
[
  {
    "id": "67b89a4b4bbe970976c1e99f",
    "name": "transaction_amount",
    "description": "Transaction amount in USD",
    "type": "numerical",
    "entity_id": "transaction",
    "feature_group_id": null,
    "tags": [],
    "metadata": {},
    "created_at": "2025-02-21T15:22:51Z",
    "updated_at": null
  }
]
```

#### Create Feature

```http
POST /features
```

Request Body:
```json
{
  "name": "transaction_amount",
  "description": "Transaction amount in USD",
  "type": "numerical",
  "entity_id": "transaction",
  "feature_group_id": null,
  "tags": [],
  "metadata": {}
}
```

Response:
```json
{
  "id": "67b89a4b4bbe970976c1e99f",
  "name": "transaction_amount",
  "description": "Transaction amount in USD",
  "type": "numerical",
  "entity_id": "transaction",
  "feature_group_id": null,
  "tags": [],
  "metadata": {},
  "created_at": "2025-02-21T15:22:51Z",
  "updated_at": null
}
```

#### Get Feature

```http
GET /features/{feature_id}
```

Response:
```json
{
  "id": "67b89a4b4bbe970976c1e99f",
  "name": "transaction_amount",
  "description": "Transaction amount in USD",
  "type": "numerical",
  "entity_id": "transaction",
  "feature_group_id": null,
  "tags": [],
  "metadata": {},
  "created_at": "2025-02-21T15:22:51Z",
  "updated_at": null
}
```

### Feature Values

#### Store Feature Value

```http
POST /features/{feature_id}/values
```

Request Body:
```json
{
  "entity_id": "transaction_123",
  "value": 150.50
}
```

Response:
```json
{
  "entity_id": "transaction_123",
  "value": 150.50,
  "timestamp": "2025-02-21T15:23:49Z"
}
```

#### Get Feature Value

```http
GET /features/{feature_id}/values/{entity_id}
```

Response:
```json
{
  "entity_id": "transaction_123",
  "value": 150.50,
  "timestamp": "2025-02-21T15:23:49Z"
}
```

## Storage Architecture

The FStore uses a dual-storage architecture:

1. **MongoDB**: Primary storage for features and feature values
   - Features collection: Stores feature metadata
   - Feature values collection: Stores feature values with timestamps

2. **Redis**: Caching layer for fast access
   - Feature cache: `feature:{feature_id}`
   - Feature value cache: `feature_value:{feature_id}:{entity_id}`

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 404: Resource not found
- 422: Validation error
- 500: Internal server error

Error responses include a detail message:
```json
{
  "detail": "Error message here"
}

# FStore API Documentation

## Overview

The FStore API provides endpoints for managing features, sources, and feature values in the feature store.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API requests require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Endpoints

### Features

#### List Features

```http
GET /features
```

Query Parameters:
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page
- `tag` (optional): Filter by tag
- `owner` (optional): Filter by owner

Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "customer_lifetime_value",
      "description": "Total value of customer purchases",
      "owner": "data_team",
      "created_at": "2025-02-20T16:02:34Z",
      "updated_at": "2025-02-20T16:02:34Z",
      "tags": ["customer", "financial"]
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 10
}
```

#### Create Feature

```http
POST /features
```

Request Body:
```json
{
  "name": "customer_lifetime_value",
  "description": "Total value of customer purchases",
  "source": {
    "type": "postgresql",
    "query": "SELECT customer_id, SUM(value) FROM orders GROUP BY customer_id",
    "update_frequency": "1h"
  },
  "tags": ["customer", "financial"],
  "owner": "data_team"
}
```

#### Get Feature

```http
GET /features/{feature_id}
```

#### Update Feature

```http
PATCH /features/{feature_id}
```

Request Body:
```json
{
  "description": "Updated description",
  "tags": ["new_tag"]
}
```

#### Delete Feature

```http
DELETE /features/{feature_id}
```

### Feature Values

#### Get Feature Values

```http
GET /features/{feature_id}/values
```

Query Parameters:
- `entity_ids`: Comma-separated list of entity IDs
- `start_time` (optional): Start time for time-based features
- `end_time` (optional): End time for time-based features

#### Write Feature Values

```http
POST /features/{feature_id}/values
```

Request Body:
```json
{
  "entity_id": "customer_123",
  "value": 1000.50,
  "timestamp": "2025-02-20T16:02:34Z"
}
```

### Sources

#### List Sources

```http
GET /sources
```

#### Add Source

```http
POST /sources
```

Request Body:
```json
{
  "type": "postgresql",
  "name": "customer_database",
  "config": {
    "host": "localhost",
    "port": 5432,
    "database": "customers",
    "user": "user",
    "password": "password"
  }
}
```

## Error Codes

- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

The API is rate limited to:
- 1000 requests per minute for GET endpoints
- 100 requests per minute for POST/PATCH/DELETE endpoints

## Versioning

The API is versioned through the URL path. The current version is v1.

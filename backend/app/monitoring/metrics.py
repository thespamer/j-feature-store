from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any
import time

# Request metrics
REQUEST_COUNT = Counter(
    'fstore_request_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'fstore_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

# Feature metrics
FEATURE_COUNT = Gauge(
    'fstore_features_total',
    'Total number of features'
)

FEATURE_VALUE_COUNT = Counter(
    'fstore_feature_values_total',
    'Total number of feature values written',
    ['feature_name']
)

FEATURE_ERROR_COUNT = Counter(
    'fstore_feature_errors_total',
    'Total number of feature processing errors',
    ['feature_name', 'error_type']
)

# Storage metrics
STORAGE_LATENCY = Histogram(
    'fstore_storage_operation_latency_seconds',
    'Storage operation latency in seconds',
    ['operation', 'storage_type']
)

STORAGE_ERROR_COUNT = Counter(
    'fstore_storage_errors_total',
    'Total number of storage errors',
    ['storage_type', 'error_type']
)

# Processing metrics
PROCESSING_TIME = Histogram(
    'fstore_processing_time_seconds',
    'Time spent processing features',
    ['feature_name']
)

PROCESSING_BATCH_SIZE = Histogram(
    'fstore_processing_batch_size',
    'Size of processed batches',
    ['feature_name']
)

class MetricsMiddleware:
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(time.time() - start_time)
        
        return response

def track_feature_processing(feature_name: str, start_time: float, batch_size: int):
    """Track feature processing metrics"""
    processing_time = time.time() - start_time
    PROCESSING_TIME.labels(feature_name=feature_name).observe(processing_time)
    PROCESSING_BATCH_SIZE.labels(feature_name=feature_name).observe(batch_size)

def track_storage_operation(operation: str, storage_type: str, start_time: float):
    """Track storage operation metrics"""
    operation_time = time.time() - start_time
    STORAGE_LATENCY.labels(
        operation=operation,
        storage_type=storage_type
    ).observe(operation_time)

def track_feature_error(feature_name: str, error_type: str):
    """Track feature processing errors"""
    FEATURE_ERROR_COUNT.labels(
        feature_name=feature_name,
        error_type=error_type
    ).inc()

def track_storage_error(storage_type: str, error_type: str):
    """Track storage errors"""
    STORAGE_ERROR_COUNT.labels(
        storage_type=storage_type,
        error_type=error_type
    ).inc()

def update_feature_count(count: int):
    """Update total feature count"""
    FEATURE_COUNT.set(count)

def track_feature_value_write(feature_name: str):
    """Track feature value writes"""
    FEATURE_VALUE_COUNT.labels(feature_name=feature_name).inc()

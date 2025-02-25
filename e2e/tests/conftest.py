import os
import pytest
import asyncio
from httpx import AsyncClient
from tenacity import retry, stop_after_attempt, wait_exponential
from kafka import KafkaProducer, KafkaConsumer
import json
from typing import AsyncGenerator, Generator

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def kafka_producer() -> Generator[KafkaProducer, None, None]:
    """Create a Kafka producer for sending test events."""
    producer = KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    yield producer
    producer.close()

@pytest.fixture(scope="session")
def kafka_consumer() -> Generator[KafkaConsumer, None, None]:
    """Create a Kafka consumer for reading processed events."""
    consumer = KafkaConsumer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        group_id='e2e_test_group'
    )
    yield consumer
    consumer.close()

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def wait_for_backend(client: AsyncClient) -> None:
    """Wait for the backend to be ready."""
    response = await client.get("/api/v1/monitoring/health")
    assert response.status_code == 200
    data = response.json()
    assert data["overall"] == "healthy"

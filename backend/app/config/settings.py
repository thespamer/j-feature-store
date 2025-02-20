from typing import Dict, Any
import os
from pathlib import Path
import yaml

# Carregar configurações do arquivo YAML
def load_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent / "datasources.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}

# Configurações padrão
DEFAULT_CONFIG = {
    "postgres": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "fstore"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres")
    },
    "kafka": {
        "bootstrap_servers": os.getenv("KAFKA_SERVERS", "localhost:9092"),
        "group_id": os.getenv("KAFKA_GROUP", "fstore_group"),
        "auto_offset_reset": "latest"
    },
    "s3": {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "region_name": os.getenv("AWS_REGION", "us-east-1"),
        "bucket": os.getenv("S3_BUCKET")
    }
}

# Carregar e mesclar configurações
config = {**DEFAULT_CONFIG, **load_config()}

# Configurações do Feature Store
FEATURE_STORE_CONFIG = {
    "storage": {
        "type": "postgres",  # Tipo de armazenamento para metadados
        "config": config["postgres"]
    },
    "feature_sources": {
        "postgres": config["postgres"],
        "kafka": config["kafka"],
        "s3": config["s3"]
    }
}

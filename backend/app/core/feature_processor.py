from datetime import datetime
from typing import Dict, Any
import time

class FeatureProcessor:
    _metrics = {
        "processed_count": 0,
        "processing_rate": 0,
        "last_processing_time": None,
        "start_time": time.time()
    }

    @classmethod
    def process_feature(cls, feature_data: Dict[str, Any]) -> None:
        """
        Processa uma feature e atualiza as métricas
        """
        # Incrementa o contador de features processadas
        cls._metrics["processed_count"] += 1
        
        # Atualiza o timestamp do último processamento
        cls._metrics["last_processing_time"] = datetime.now().isoformat()
        
        # Calcula a taxa de processamento (features/segundo)
        elapsed_time = time.time() - cls._metrics["start_time"]
        if elapsed_time > 0:
            cls._metrics["processing_rate"] = round(cls._metrics["processed_count"] / elapsed_time, 2)

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """
        Retorna as métricas atuais do processador
        """
        return cls._metrics.copy()

    @classmethod
    def reset_metrics(cls) -> None:
        """
        Reseta todas as métricas
        """
        cls._metrics = {
            "processed_count": 0,
            "processing_rate": 0,
            "last_processing_time": None,
            "start_time": time.time()
        }

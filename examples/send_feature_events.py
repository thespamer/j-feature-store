import requests
import json
from datetime import datetime
import random
import time

def send_feature_value(feature_id: str, entity_id: str, value: float):
    """
    Envia um valor de feature via API
    """
    url = "http://localhost:8000/api/v1/features/{}/values".format(feature_id)
    
    payload = {
        "entity_id": entity_id,
        "value": value,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    response = requests.post(url, json=payload)
    return response.status_code == 200

def simulate_events():
    """
    Simula eventos de features para demonstração
    """
    # IDs das features que queremos atualizar
    feature_configs = [
        {
            "feature_id": "customer_purchase_amount",
            "entity_ids": ["customer_1", "customer_2", "customer_3"],
            "min_value": 10.0,
            "max_value": 1000.0
        },
        {
            "feature_id": "product_stock_level",
            "entity_ids": ["product_1", "product_2"],
            "min_value": 0.0,
            "max_value": 100.0
        }
    ]
    
    while True:
        for config in feature_configs:
            for entity_id in config["entity_ids"]:
                # Gera um valor aleatório
                value = random.uniform(config["min_value"], config["max_value"])
                
                try:
                    success = send_feature_value(
                        config["feature_id"], 
                        entity_id, 
                        value
                    )
                    
                    print(f"Enviado: feature={config['feature_id']}, "
                          f"entity={entity_id}, value={value:.2f}, "
                          f"success={success}")
                          
                except Exception as e:
                    print(f"Erro ao enviar evento: {str(e)}")
            
        # Espera 5 segundos antes do próximo lote
        time.sleep(5)

if __name__ == "__main__":
    print("Iniciando simulação de eventos...")
    try:
        simulate_events()
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário")

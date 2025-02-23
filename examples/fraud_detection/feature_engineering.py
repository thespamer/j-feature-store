from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import requests
import json

class FeatureStoreClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def create_feature_group(self, name, description, entity_type, features=None, tags=None, frequency="realtime"):
        """Cria um novo grupo de features"""
        url = f"{self.base_url}/api/v1/feature-groups"
        data = {
            "name": name,
            "description": description,
            "entity_id": entity_type,
            "entity_type": entity_type,
            "tags": tags or [],
            "frequency": frequency,
            "features": features or []
        }
        response = requests.post(url, json=data)
        if response.status_code in [200, 201]:
            print(f"Created feature group: {name}")
            return response.json()
        else:
            print(f"Failed to create feature group: {response.text}")
            return None
        
    def get_historical_features(self, feature_group, entity_id, start_time, end_time):
        """Busca features históricas via API REST"""
        url = f"{self.base_url}/api/v1/feature-groups/{feature_group}/features"
        params = {
            'entity_id': entity_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data.get('features', []))
        return pd.DataFrame()
        
    def store_features(self, feature_group, entity_id, features, metadata=None):
        """Armazena features via API REST"""
        url = f"{self.base_url}/api/v1/features"
        
        # Converte o dicionário de features em uma lista de FeatureValue
        feature_values = []
        timestamp = metadata.get('timestamp') if metadata else None
        
        for name, value in features.items():
            feature_data = {
                "id": f"{feature_group}_{name}",
                "name": name,
                "description": f"Feature {name} do grupo {feature_group}",
                "type": "numerical" if isinstance(value, (int, float)) else "categorical",
                "entity_id": entity_id,
                "feature_group_id": feature_group,
                "value": float(value) if isinstance(value, (int, float)) else str(value),
                "timestamp": timestamp or datetime.now().isoformat()
            }
            feature_values.append(feature_data)
        
        # Envia as features uma a uma
        for feature in feature_values:
            response = requests.post(url, json=feature)
            if response.status_code in [200, 201]:
                print(f"Stored feature {feature['name']} for {entity_id} in group {feature_group}")
            else:
                print(f"Failed to store feature {feature['name']}: {response.text}")

class FraudFeatureEngineer:
    def __init__(self):
        self.feature_store = FeatureStoreClient()
        
    def calculate_transaction_features(self, transaction_data, historical_window='1h'):
        """Calcula features para detecção de fraude baseadas em uma transação e seu histórico"""
        card_id = transaction_data['card_id']
        timestamp = datetime.fromisoformat(transaction_data['timestamp'])
        amount = transaction_data['amount']
        
        # Busca histórico de transações do cartão
        historical_txs = self.feature_store.get_historical_features(
            feature_group="credit_card_transactions",
            entity_id=card_id,
            start_time=timestamp - timedelta(hours=1),
            end_time=timestamp
        )
        
        # Features básicas da transação
        features = {
            'transaction_amount': amount,
            'merchant_category': transaction_data['merchant_category'],
            'merchant_country': transaction_data['merchant_country'],
            'transaction_hour': timestamp.hour,
            'transaction_day': timestamp.day,
            'is_weekend': timestamp.weekday() >= 5
        }
        
        # Se não há histórico, retorna features padrão
        if len(historical_txs) == 0:
            features.update({
                'tx_count_1h': 0,
                'total_amount_1h': 0,
                'avg_amount_1h': 0,
                'std_amount_1h': 0,
                'unique_countries_1h': 0,
                'unique_merchants_1h': 0,
                'max_amount_1h': 0,
                'min_amount_1h': 0,
                'amount_velocity': 0,
                'small_tx_ratio': 0,
                'amount_ratio_to_avg': 1.0,
                'small_amount_variations': 0,
                'country_change_ratio': 0
            })
            return features
        
        # Adiciona a transação atual ao histórico para cálculos
        current_tx = pd.DataFrame([{
            'timestamp': timestamp,
            'amount': amount,
            'merchant': transaction_data['merchant'],
            'merchant_country': transaction_data['merchant_country']
        }])
        all_txs = pd.concat([historical_txs, current_tx]).sort_values('timestamp')
        
        # Features baseadas em contagem e valores
        features.update({
            'tx_count_1h': len(historical_txs),
            'total_amount_1h': historical_txs['amount'].sum(),
            'avg_amount_1h': historical_txs['amount'].mean(),
            'std_amount_1h': historical_txs['amount'].std(),
            'unique_countries_1h': historical_txs['merchant_country'].nunique(),
            'unique_merchants_1h': historical_txs['merchant'].nunique(),
            'max_amount_1h': historical_txs['amount'].max(),
            'min_amount_1h': historical_txs['amount'].min(),
            'amount_velocity': self._calculate_amount_velocity(all_txs['amount'])
        })
        
        # Features específicas para detecção de padrões de fraude
        small_threshold = 20  # Transações abaixo de €20 são consideradas pequenas
        small_txs = historical_txs[historical_txs['amount'] <= small_threshold]
        features['small_tx_ratio'] = len(small_txs) / len(historical_txs) if len(historical_txs) > 0 else 0
        
        # Razão entre valor atual e média histórica
        if features['avg_amount_1h'] > 0:
            features['amount_ratio_to_avg'] = amount / features['avg_amount_1h']
        else:
            features['amount_ratio_to_avg'] = 1.0 if amount <= small_threshold else 2.0
        
        # Detecção de variações pequenas nos valores
        if len(all_txs) > 1:
            diffs = np.diff(all_txs['amount'].values)
            small_variations = np.abs(diffs) < (0.1 * all_txs['amount'].mean())  # Variações menores que 10% da média
            features['small_amount_variations'] = np.mean(small_variations)
        else:
            features['small_amount_variations'] = 0
        
        # Razão de mudança de países
        if len(all_txs) > 1:
            country_changes = (all_txs['merchant_country'] != all_txs['merchant_country'].shift()).sum()
            features['country_change_ratio'] = country_changes / (len(all_txs) - 1)
        else:
            features['country_change_ratio'] = 0
        
        # Armazena a transação no histórico com grupo de features específico
        self.feature_store.store_features(
            feature_group="fraud_detection_features",  # Grupo específico para features de detecção
            entity_id=card_id,
            features=features,
            metadata={
                'timestamp': timestamp.isoformat(),
                'transaction_id': transaction_data.get('transaction_id', ''),
                'merchant': transaction_data['merchant'],
                'merchant_country': transaction_data['merchant_country']
            }
        )
        
        # Armazena também os dados brutos da transação
        self.feature_store.store_features(
            feature_group="credit_card_transactions",
            entity_id=card_id,
            features={
                'timestamp': timestamp.isoformat(),
                'amount': amount,
                'merchant': transaction_data['merchant'],
                'merchant_country': transaction_data['merchant_country']
            }
        )
        
        return features
    
    def _calculate_amount_velocity(self, amounts):
        """Calcula a velocidade de mudança nos valores das transações"""
        if len(amounts) < 2:
            return 0
        time_diffs = np.arange(len(amounts))  # Assume intervalos uniformes
        return np.polyfit(time_diffs, amounts, 1)[0]  # Retorna a inclinação da linha de tendência

if __name__ == "__main__":
    # Exemplo de uso
    engineer = FraudFeatureEngineer()
    
    # Exemplo de transação
    transaction = {
        "transaction_id": "123",
        "card_id": "456",
        "timestamp": datetime.now().isoformat(),
        "amount": 999.99,
        "merchant": "Steam",
        "merchant_category": "gaming",
        "merchant_country": "US"
    }
    
    # Calcula e armazena features
    features = engineer.calculate_transaction_features(transaction)
    print("Features calculadas:")
    for name, value in features.items():
        print(f"{name}: {value}")

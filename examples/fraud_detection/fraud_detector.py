import json
from datetime import datetime
import xgboost as xgb
from feature_engineering import FraudFeatureEngineer, FeatureStoreClient

class FraudDetector:
    def __init__(self):
        self.feature_engineer = FraudFeatureEngineer()
        self.feature_store = FeatureStoreClient()
        self.model = self._load_model()
        
        # Limiares de risco ajustados para maior sensibilidade
        self.risk_thresholds = {
            'high': 0.7,    # Era 0.8
            'medium': 0.4,  # Era 0.5
            'low': 0.1      # Era 0.2
        }
    
    def _load_model(self):
        """Carrega o modelo XGBoost treinado"""
        try:
            model = xgb.Booster({'nthread': 4})  # init model
            model.load_model('fraud_detection_model.json')
            return model
        except:
            print("Modelo não encontrado. Usando apenas regras de negócio para detecção.")
            return None
    
    def analyze_transaction(self, transaction):
        """Analisa uma transação em tempo real para detectar fraude"""
        # Extrai features da transação
        features = self.feature_engineer.calculate_transaction_features(transaction)
        
        # Avalia padrões de risco baseados em regras
        risk_patterns = self._evaluate_risk_patterns(transaction, features)
        
        # Calcula score de fraude usando o modelo (se disponível)
        fraud_score = self._calculate_fraud_score(features)
        
        # Determina o nível de risco baseado no score e padrões
        risk_level = self._determine_risk_level(fraud_score, risk_patterns)
        
        # Prepara o resultado da análise
        analysis_result = {
            'transaction_id': transaction.get('transaction_id', ''),
            'card_id': transaction['card_id'],
            'timestamp': transaction['timestamp'],
            'amount': transaction['amount'],
            'merchant': transaction['merchant'],
            'merchant_country': transaction['merchant_country'],
            'fraud_score': fraud_score,
            'risk_level': risk_level,
            'risk_patterns': risk_patterns,
            'features': features  # Inclui as features calculadas no resultado
        }
        
        # Armazena o resultado da análise
        self.feature_store.store_features(
            feature_group="fraud_analysis_results",
            entity_id=transaction['card_id'],
            features=analysis_result,
            metadata={
                'timestamp': transaction['timestamp'],
                'transaction_id': transaction.get('transaction_id', ''),
                'risk_level': risk_level,
                'fraud_score': fraud_score
            }
        )
        
        return analysis_result
    
    def _evaluate_risk_patterns(self, transaction, features):
        """Avalia padrões específicos de risco baseados em regras de negócio"""
        risk_patterns = []
        
        # Padrão 1: Múltiplas transações pequenas seguidas de uma grande
        if features.get('tx_count_1h', 0) > 2 and \
           features.get('small_tx_ratio', 0) > 0.5 and \
           features.get('amount_ratio_to_avg', 0) > 3:  # Eram 3, 0.7 e 5 respectivamente
            risk_patterns.append({
                'pattern': 'multiple_small_large',
                'description': 'Múltiplas transações pequenas seguidas de uma grande',
                'severity': 'high'
            })
        
        # Padrão 2: Transações em diferentes países em curto período
        if features.get('unique_countries_1h', 0) > 1:  # Era 2
            risk_patterns.append({
                'pattern': 'geographic_spread',
                'description': 'Transações em múltiplos países em curto período',
                'severity': 'high'
            })
        
        # Padrão 3: Tentativas repetidas com pequenas variações
        if features.get('small_amount_variations', 0) > 0.3:  # Era 0.5
            risk_patterns.append({
                'pattern': 'amount_variations',
                'description': 'Múltiplas tentativas com pequenas variações no valor',
                'severity': 'medium'
            })
        
        # Padrão 4: Transação com valor muito acima da média
        if features.get('amount_ratio_to_avg', 0) > 5:  # Era 10
            risk_patterns.append({
                'pattern': 'unusual_amount',
                'description': 'Valor da transação muito acima do padrão',
                'severity': 'medium'
            })
        
        # Padrão 5: Alta velocidade de transações
        if features.get('tx_count_1h', 0) > 3:  # Era 5
            risk_patterns.append({
                'pattern': 'high_velocity',
                'description': 'Alta frequência de transações',
                'severity': 'medium'
            })
        
        return risk_patterns
    
    def _calculate_fraud_score(self, features):
        """Calcula o score de fraude usando o modelo ou regras"""
        if self.model:
            # Prepara features para o modelo
            feature_vector = xgb.DMatrix([list(features.values())])
            return float(self.model.predict(feature_vector)[0])
        else:
            # Cálculo simplificado baseado em regras
            score = 0.0
            
            # Pontuação baseada em transações pequenas seguidas de grande
            if features.get('small_tx_ratio', 0) > 0.5 and features.get('amount_ratio_to_avg', 0) > 3:
                score += 0.4
            
            # Pontuação baseada em dispersão geográfica
            if features.get('unique_countries_1h', 0) > 1:
                score += 0.3
            
            # Pontuação baseada em variações de valor
            if features.get('small_amount_variations', 0) > 0.3:
                score += 0.2
            
            # Pontuação baseada em velocidade de transações
            if features.get('tx_count_1h', 0) > 3:
                score += 0.1
            
            return min(score, 1.0)
    
    def _determine_risk_level(self, fraud_score, risk_patterns):
        """Determina o nível de risco baseado no score e padrões identificados"""
        # Considera o padrão mais severo
        pattern_severity = 'safe'
        for pattern in risk_patterns:
            if pattern['severity'] == 'high':
                pattern_severity = 'high'
                break
            elif pattern['severity'] == 'medium' and pattern_severity != 'high':
                pattern_severity = 'medium'
            elif pattern['severity'] == 'low' and pattern_severity == 'safe':
                pattern_severity = 'low'
        
        # Combina score com severidade dos padrões
        if fraud_score >= self.risk_thresholds['high'] or pattern_severity == 'high':
            return 'high'
        elif fraud_score >= self.risk_thresholds['medium'] or pattern_severity == 'medium':
            return 'medium'
        elif fraud_score >= self.risk_thresholds['low'] or pattern_severity == 'low':
            return 'low'
        return 'safe'

if __name__ == "__main__":
    # Exemplo de uso
    detector = FraudDetector()
    
    # Exemplo de transação suspeita
    suspicious_transaction = {
        "transaction_id": "tx_123",
        "card_id": "card_456",
        "timestamp": datetime.now().isoformat(),
        "amount": 1999.99,
        "merchant": "Unknown Store",
        "merchant_category": "retail",
        "merchant_country": "RO",
        "currency": "EUR"
    }
    
    # Analisa a transação
    result = detector.analyze_transaction(suspicious_transaction)
    
    print("\nResultado da análise de fraude:")
    print(json.dumps(result, indent=2))

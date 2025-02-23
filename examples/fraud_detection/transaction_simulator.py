import random
import time
from datetime import datetime, timedelta
from faker import Faker
import json
from fraud_detector import FraudDetector
from collections import defaultdict

fake = Faker()

class TransactionGenerator:
    def __init__(self):
        self.merchants = [
            {"name": "Amazon", "category": "e-commerce", "country": "US"},
            {"name": "Steam", "category": "gaming", "country": "US"},
            {"name": "Carrefour", "category": "retail", "country": "FR"},
            {"name": "Uber", "category": "transport", "country": "GB"},
            {"name": "Booking.com", "category": "travel", "country": "NL"}
        ]
        
        # Padrões de fraude conhecidos
        self.fraud_patterns = {
            "pattern1": {
                "description": "Múltiplas transações pequenas seguidas de uma grande",
                "small_tx_count": lambda: random.randint(3, 7),
                "small_amount": lambda: random.uniform(1, 20),
                "large_amount": lambda: random.uniform(500, 2000)
            },
            "pattern2": {
                "description": "Transações em diferentes países em curto período",
                "tx_count": lambda: random.randint(2, 4),
                "amount": lambda: random.uniform(100, 1000),
                "time_window": timedelta(hours=1)
            },
            "pattern3": {
                "description": "Tentativas repetidas com pequenas variações no valor",
                "base_amount": lambda: random.uniform(100, 500),
                "variation": lambda: random.uniform(-5, 5),
                "attempts": lambda: random.randint(3, 5)
            }
        }

    def generate_card(self):
        """Gera dados de cartão de crédito"""
        return {
            "card_id": fake.uuid4(),
            "card_number": fake.credit_card_number(),
            "card_type": random.choice(["VISA", "MASTERCARD", "AMEX"]),
            "expiry_date": fake.credit_card_expire(),
            "cvv": fake.credit_card_security_code(),
            "holder_name": fake.name(),
            "holder_country": fake.country_code()
        }

    def generate_legitimate_transaction(self, card):
        """Gera uma transação legítima"""
        merchant = random.choice(self.merchants)
        return {
            "transaction_id": fake.uuid4(),
            "timestamp": datetime.now().isoformat(),
            "card_id": card["card_id"],
            "merchant": merchant["name"],
            "merchant_category": merchant["category"],
            "merchant_country": merchant["country"],
            "amount": round(random.uniform(10, 500), 2),
            "currency": "EUR",
            "is_fraud": False
        }

    def generate_fraud_pattern1(self, card):
        """Gera padrão de fraude: múltiplas transações pequenas seguidas de uma grande"""
        pattern = self.fraud_patterns["pattern1"]
        transactions = []
        
        # Pequenas transações
        for _ in range(pattern["small_tx_count"]()):
            merchant = random.choice(self.merchants)
            transactions.append({
                "transaction_id": fake.uuid4(),
                "timestamp": datetime.now().isoformat(),
                "card_id": card["card_id"],
                "merchant": merchant["name"],
                "merchant_category": merchant["category"],
                "merchant_country": merchant["country"],
                "amount": round(pattern["small_amount"](), 2),
                "currency": "EUR",
                "is_fraud": True,
                "fraud_pattern": "multiple_small_large"
            })
            time.sleep(0.5)  # Pequeno delay entre transações
        
        # Grande transação final
        merchant = random.choice(self.merchants)
        transactions.append({
            "transaction_id": fake.uuid4(),
            "timestamp": datetime.now().isoformat(),
            "card_id": card["card_id"],
            "merchant": merchant["name"],
            "merchant_category": merchant["category"],
            "merchant_country": merchant["country"],
            "amount": round(pattern["large_amount"](), 2),
            "currency": "EUR",
            "is_fraud": True,
            "fraud_pattern": "multiple_small_large"
        })
        
        return transactions

    def generate_fraud_pattern2(self, card):
        """Gera padrão de fraude: transações em diferentes países em curto período"""
        pattern = self.fraud_patterns["pattern2"]
        transactions = []
        countries = random.sample([m["country"] for m in self.merchants], pattern["tx_count"]())
        
        for country in countries:
            merchant = next(m for m in self.merchants if m["country"] == country)
            transactions.append({
                "transaction_id": fake.uuid4(),
                "timestamp": datetime.now().isoformat(),
                "card_id": card["card_id"],
                "merchant": merchant["name"],
                "merchant_category": merchant["category"],
                "merchant_country": country,
                "amount": round(pattern["amount"](), 2),
                "currency": "EUR",
                "is_fraud": True,
                "fraud_pattern": "geographic_spread"
            })
            time.sleep(0.5)
        
        return transactions

    def simulate_transactions(self, num_cards=5, fraud_probability=0.2):
        """Simula um conjunto de transações com possibilidade de fraude"""
        cards = [self.generate_card() for _ in range(num_cards)]
        all_transactions = []
        
        for card in cards:
            # Decide se este cartão terá fraude
            has_fraud = random.random() < fraud_probability
            
            if has_fraud:
                # Escolhe um padrão de fraude aleatório
                fraud_pattern = random.choice([self.generate_fraud_pattern1, self.generate_fraud_pattern2])
                fraud_transactions = fraud_pattern(card)
                all_transactions.extend(fraud_transactions)
            
            # Gera algumas transações legítimas
            num_legitimate = random.randint(3, 8)
            legitimate_transactions = [self.generate_legitimate_transaction(card) for _ in range(num_legitimate)]
            all_transactions.extend(legitimate_transactions)
        
        return all_transactions

if __name__ == "__main__":
    generator = TransactionGenerator()
    detector = FraudDetector()
    
    print("Iniciando simulação de transações...")
    transactions = generator.simulate_transactions(num_cards=5, fraud_probability=0.4)
    
    # Agrupa transações por cartão
    card_transactions = defaultdict(list)
    for tx in transactions:
        card_transactions[tx['card_id']].append(tx)
    
    print(f"\nGeradas {len(transactions)} transações em {len(card_transactions)} cartões")
    
    print("\nAnalisando padrões de transação por cartão:")
    for card_id, card_txs in card_transactions.items():
        fraud_txs = [tx for tx in card_txs if tx.get('is_fraud', False)]
        if fraud_txs:
            print(f"\nCartão {card_id}:")
            print(f"Total de transações: {len(card_txs)}")
            print(f"Transações fraudulentas: {len(fraud_txs)}")
            print("\nSequência de transações:")
            for tx in sorted(card_txs, key=lambda x: x['timestamp']):
                print(f"{'[FRAUDE] ' if tx.get('is_fraud') else '         '}€{tx['amount']:8.2f} em {tx['merchant']} ({tx['merchant_country']})")
            print("-" * 50)
    
    print("\nAnalisando transações com detector de fraude...")
    detected_frauds = []
    
    for tx in transactions:
        result = detector.analyze_transaction(tx)
        if result['risk_level'] != 'safe':
            detected_frauds.append((tx, result))
    
    if detected_frauds:
        print(f"\nDetectadas {len(detected_frauds)} transações suspeitas:")
        for tx, result in detected_frauds:
            print(f"\nTransação suspeita detectada!")
            print(f"ID: {tx['transaction_id']}")
            print(f"Valor: €{tx['amount']:.2f}")
            print(f"Comerciante: {tx['merchant']} ({tx['merchant_country']})")
            print(f"Score de Fraude: {result['fraud_score']:.2f}")
            print(f"Nível de Risco: {result['risk_level'].upper()}")
            if result['risk_patterns']:
                print("Padrões de risco detectados:")
                for pattern in result['risk_patterns']:
                    print(f"- {pattern['description']} (Severidade: {pattern['severity']})")
            print(f"É realmente fraude? {'Sim' if tx.get('is_fraud', False) else 'Não'}")
            print("-" * 50)
    
    print("\nResumo da análise:")
    total_frauds = sum(1 for tx in transactions if tx.get('is_fraud', False))
    detected_count = len(detected_frauds)
    true_positives = sum(1 for tx, _ in detected_frauds if tx.get('is_fraud', False))
    false_positives = detected_count - true_positives
    false_negatives = total_frauds - true_positives
    
    print(f"Total de transações: {len(transactions)}")
    print(f"Transações fraudulentas reais: {total_frauds} ({(total_frauds/len(transactions))*100:.1f}%)")
    print(f"Transações suspeitas detectadas: {detected_count}")
    print(f"Verdadeiros positivos: {true_positives}")
    print(f"Falsos positivos: {false_positives}")
    print(f"Falsos negativos: {false_negatives}")
    if detected_count > 0:
        precision = true_positives / detected_count
        recall = true_positives / total_frauds if total_frauds > 0 else 0
        print(f"Precisão: {precision:.1%}")
        print(f"Recall: {recall:.1%}")

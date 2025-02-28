# Guia do Analista ML: JStore Feature Store

Este guia prático vai te ajudar a começar a usar a JStore Feature Store para seus projetos de ML.

## Pré-requisitos

- Seus dados já estão em um banco PostgreSQL
- A JStore Feature Store está instalada e rodando (http://localhost:3000)

## 1. Organização das Features

Primeiro, organize suas features em **Feature Groups**. Um Feature Group é um conjunto de features relacionadas, por exemplo:
- `customer_features`: features relacionadas ao cliente
- `transaction_features`: features relacionadas a transações
- `product_features`: features relacionadas a produtos

## 2. Criando Features via Interface Web

1. Acesse a interface web em `http://localhost:3000`

2. Para cada grupo de features que você precisa:
   - No menu lateral, clique em "Feature Groups"
   - Clique no botão "Novo Grupo de Features"
   - Preencha:
     - Nome (ex: "customer_features")
     - Descrição
     - Entity Type (ex: "customer")
     - Frequência de atualização (ex: "daily")

3. Para cada feature individual:
   - No menu lateral, clique em "Features"
   - Clique no botão "Nova Feature"
   - Preencha:
     - Nome (ex: "avg_order_value")
     - Tipo (float, int, string, etc)
     - Descrição
     - Entity ID (ex: "customer_id")
     - Selecione o Feature Group

4. Na seção "Transformação SQL":
   - Expanda a seção clicando no título
   - Escreva sua query SQL que calcula a feature
   - Especifique a coluna de saída que contém o valor da feature

Exemplo de transformação SQL para `avg_order_value`:
```sql
SELECT 
  customer_id,
  AVG(total_amount) as avg_order_value,
  COUNT(*) as order_count,
  MAX(order_date) as last_order_date
FROM orders
GROUP BY customer_id
```

## 3. Criando o Pipeline

1. Na página de Feature Groups, encontre o grupo para o qual você quer criar o pipeline
2. Na seção "Pipelines" do grupo, clique no botão "Novo Pipeline"
3. Configure:
   - Nome do pipeline
   - Frequência de execução (diária, horária, etc)
   - Query SQL fonte (sua query do PostgreSQL)
   - Outros parâmetros como timeout, retry, etc
4. Clique em "Criar" para salvar o pipeline

## 4. Usando as Features para ML

Primeiro, instale o cliente Python da JStore:
```bash
pip install jstore-client
```

### Configuração do Cliente

```python
from jstore import FeatureStore

# Para uso local
fs = FeatureStore(host="localhost", port=8000)

# Para uso remoto
fs = FeatureStore(
    host="seu-feature-store.exemplo.com",  # URL do seu servidor
    port=443,                              # Porta (443 para HTTPS)
    api_key="seu-api-key",                # Chave de API para autenticação
    use_ssl=True                          # Usar HTTPS
)

# Você também pode usar variáveis de ambiente:
# export JSTORE_HOST=seu-feature-store.exemplo.com
# export JSTORE_API_KEY=seu-api-key
fs = FeatureStore.from_env()
```

### Para Treinamento (Offline)

```python
# Busca features para treinar seu modelo
training_features = fs.get_feature_group(
    name="customer_features",
    start_date="2025-01-01",
    end_date="2025-02-28"
)

# Opções avançadas
training_features = fs.get_feature_group(
    name="customer_features",
    start_date="2025-01-01",
    end_date="2025-02-28",
    batch_size=10000,           # Tamanho do batch para memória
    as_of_date="2025-01-15",   # Point-in-time features
    include_deleted=False,      # Ignorar features deletadas
    version="1.0.0"            # Versão específica do feature group
)

# Converte para DataFrame
df = training_features.to_pandas()

# Use no seu modelo
X = df[['avg_order_value', 'order_count', 'days_since_last_order']]
y = df['target']
```

### Para Inferência (Online)

```python
# Busca features em tempo real para um único ID
customer_features = fs.get_online_features(
    feature_group="customer_features",
    entity_ids=["customer_123"]
)

# Busca features para múltiplos IDs
customer_features = fs.get_online_features(
    feature_group="customer_features",
    entity_ids=["customer_123", "customer_456", "customer_789"]
)

# Com timeout e retry
customer_features = fs.get_online_features(
    feature_group="customer_features",
    entity_ids=["customer_123"],
    timeout_ms=1000,           # Timeout em milissegundos
    max_retries=3,            # Número máximo de tentativas
    fallback="latest"         # Em caso de erro, usa último valor conhecido
)

# Faça a predição
prediction = model.predict(customer_features)
```

### Exemplo com Pipeline ML Completo

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from jstore import FeatureStore

# 1. Inicializa o cliente
fs = FeatureStore.from_env()

# 2. Obtém as features
features = fs.get_feature_group("customer_features")
df = features.to_pandas()

# 3. Prepara os dados
X = df[['avg_order_value', 'order_count', 'days_since_last_order']]
y = df['is_churned']

# 4. Split treino/teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 5. Treina o modelo
model = RandomForestClassifier()
model.fit(X_train, y_train)

# 6. Função de inferência
def predict_churn(customer_id: str) -> float:
    # Busca features online
    features = fs.get_online_features(
        feature_group="customer_features",
        entity_ids=[customer_id]
    )
    
    # Faz predição
    return model.predict_proba(features)[0, 1]  # Prob. de churn

# 7. Uso
churn_prob = predict_churn("customer_123")
print(f"Probabilidade de churn: {churn_prob:.2%}")
```

### Tratamento de Erros

```python
from jstore.exceptions import (
    FeatureStoreConnectionError,
    FeatureNotFoundError,
    FeatureGroupNotFoundError
)

try:
    features = fs.get_online_features(
        feature_group="customer_features",
        entity_ids=["customer_123"]
    )
except FeatureStoreConnectionError as e:
    print(f"Erro de conexão: {e}")
    # Use fallback local ou cache
except FeatureNotFoundError as e:
    print(f"Feature não encontrada: {e}")
    # Use valor default
except FeatureGroupNotFoundError as e:
    print(f"Feature group não encontrado: {e}")
    # Logging e alerta
```

## 5. Monitoramento

Na interface web:
1. Clique em "Monitoring" no menu lateral
2. Aqui você pode:
   - Visualizar estatísticas das features
   - Monitorar a qualidade dos dados
   - Verificar o status dos pipelines
   - Ver logs de execução

## Dicas Importantes

1. **Versionamento**: Sempre documente suas features com descrições claras e tags

2. **Performance**: 
   - Para features que mudam pouco, use frequência "daily"
   - Para features em tempo real, use "hourly" ou menor

3. **Validação**:
   - Adicione regras de validação nas features (min/max, tipos, etc)
   - Monitore drift nas distribuições

4. **Organização**:
   - Agrupe features relacionadas no mesmo Feature Group
   - Use tags para categorizar (ex: "risk", "engagement", "financial")

## Exemplos Práticos

Veja exemplos completos em:
- `/examples/fraud_detection/`: Sistema de detecção de fraude
- `/examples/customer_segmentation/`: Segmentação de clientes
- `/examples/product_recommendation/`: Recomendação de produtos

## Precisa de Ajuda?

- Documentação completa: `/docs/`
- Tutoriais passo a passo: `/docs/TUTORIAL.md`
- Referência da API: `/docs/API.md`
- Arquitetura e conceitos: `/docs/ARCHITECTURE.md`

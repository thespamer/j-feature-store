# Tutorial: J Feature Store para Cientistas de Dados e Analistas de ML

## Índice
1. [Introdução](#introdução)
2. [Por que usar uma Feature Store?](#por-que-usar-uma-feature-store)
3. [Conceitos Fundamentais](#conceitos-fundamentais)
4. [Primeiros Passos](#primeiros-passos)
5. [Casos de Uso Práticos](#casos-de-uso-práticos)
6. [Melhores Práticas](#melhores-práticas)
7. [Troubleshooting](#troubleshooting)
8. [Feature Groups](#feature-groups)

## Introdução

A J Feature Store é uma plataforma moderna de gerenciamento de features para Machine Learning, projetada para simplificar o ciclo de vida completo das features - desde a criação até o deploy em produção. Este tutorial irá guiá-lo através dos conceitos essenciais e casos de uso práticos.

### Para quem é este tutorial?
- Cientistas de Dados
- Engenheiros de ML
- Analistas de Dados
- Qualquer profissional trabalhando com features para ML

## Por que usar uma Feature Store?

### Desafios Comuns em ML
- Inconsistência entre features de treino e produção
- Duplicação de código e esforço
- Dificuldade em rastrear a linhagem das features
- Problemas de performance em produção
- Falta de documentação e governança

### Como a Feature Store Resolve
1. **Consistência**: Garante que as mesmas transformações sejam aplicadas em treino e produção
2. **Reutilização**: Features podem ser compartilhadas entre diferentes projetos
3. **Governança**: Rastreabilidade completa da origem até o uso
4. **Performance**: Otimização automática para diferentes casos de uso
5. **Colaboração**: Documentação centralizada e descoberta de features

## Conceitos Fundamentais

### 1. Features
Uma feature é qualquer sinal ou característica usada em modelos de ML. Exemplos:
- Média de compras nos últimos 7 dias
- Categoria mais frequente de produtos visualizados
- Tempo desde a última interação

### 2. Transformações
Operações que transformam dados brutos em features. Tipos suportados:
- SQL Queries
- Agregações temporais
- Joins entre diferentes fontes

### 3. Entity
O objeto principal ao qual as features se relacionam. Exemplos:
- customer_id
- product_id
- store_id

## Primeiros Passos

### 1. Acessando a Interface

```python
# Se estiver usando localmente
FEATURE_STORE_URL = "http://localhost:3000"

# Se estiver usando uma instância remota
FEATURE_STORE_URL = "https://feature-store.sua-empresa.com"
```

### 2. Criando sua Primeira Feature

#### Via Interface Web
1. Acesse a página Features
2. Clique no botão "+"
3. Preencha:
   ```
   Nome: customer_purchase_7d_avg
   Descrição: Média de compras nos últimos 7 dias
   Tipo: Numerical
   Entity ID: customer_id
   ```
4. Adicione a transformação SQL:
   ```sql
   SELECT
     customer_id,
     AVG(purchase_amount) as purchase_7d_avg
   FROM transactions
   WHERE 
     transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
   GROUP BY customer_id
   ```

#### Via Python
```python
from j_feature_store import FeatureStoreClient

client = FeatureStoreClient(FEATURE_STORE_URL)

feature = client.create_feature(
    name="customer_purchase_7d_avg",
    description="Média de compras nos últimos 7 dias",
    type="numerical",
    entity_id="customer_id",
    transformation={
        "sql_query": """
            SELECT
                customer_id,
                AVG(purchase_amount) as purchase_7d_avg
            FROM transactions
            WHERE 
                transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
            GROUP BY customer_id
        """,
        "aggregation_window": "7d"
    }
)
```

## Casos de Uso Práticos

### 1. Previsão de Churn em Tempo Real

#### Cenário
Uma empresa de SaaS precisa identificar clientes com risco de churn para ações proativas.

#### Implementação
```python
# 1. Criar grupo de features para churn
churn_group = client.create_feature_group(
    name="churn_prediction",
    description="Features para modelo de churn",
    entity_type="customer",
    frequency="daily",
    online_enabled=True  # Importante para inferência em tempo real
)

# 2. Definir features relevantes
features = [
    {
        "name": "days_since_last_login",
        "type": "numerical",
        "transformation": """
            WITH user_avg AS (
                SELECT AVG(amount) as avg_amount
                FROM transactions
                WHERE user_id = :user_id
                AND timestamp >= NOW() - INTERVAL '30 days'
            )
            SELECT amount / user_avg.avg_amount
            FROM transactions
            CROSS JOIN user_avg
            WHERE id = :transaction_id
        """
    },
    {
        "name": "support_tickets_last_30d",
        "type": "numerical",
        "transformation": """
            SELECT COUNT(*) 
            FROM support_tickets 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
    },
    {
        "name": "usage_trend",
        "type": "numerical",
        "transformation": """
            SELECT 
                (curr_month_usage - prev_month_usage) / prev_month_usage 
            FROM usage_metrics
        """
    }
]

# 3. Registrar features e adicionar ao grupo
for feature in features:
    feature_id = client.create_feature(feature)
    client.add_feature_to_group(churn_group.id, feature_id)

# 4. Uso em produção
def predict_churn(customer_id: str):
    # Obter features em tempo real
    features = client.get_online_features(
        feature_group="churn_prediction",
        entity_id=customer_id
    )
    
    # Fazer predição
    prediction = model.predict(features)
    return prediction
```

### 2. Recomendação de Produtos Personalizada

#### Cenário
E-commerce que precisa recomendar produtos baseados no histórico do cliente.

#### Implementação
```python
# 1. Criar grupos de features para diferentes aspectos
client.create_feature_group(
    name="user_preferences",
    description="Preferências históricas do usuário",
    entity_type="customer",
    features=[
        "favorite_categories",
        "price_sensitivity",
        "brand_affinity"
    ]
)

client.create_feature_group(
    name="product_characteristics",
    description="Características dos produtos",
    entity_type="product",
    features=[
        "category_embedding",
        "price_segment",
        "popularity_score"
    ]
)

# 2. Feature para similaridade produto-usuário
def calculate_user_product_similarity():
    return """
        SELECT 
            u.user_id,
            p.product_id,
            COSINE_SIMILARITY(
                u.preference_vector,
                p.product_vector
            ) as similarity_score
        FROM user_features u
        CROSS JOIN product_features p
    """

# 3. Uso em produção
def get_recommendations(user_id: str, top_k: int = 5):
    # Obter features do usuário
    user_features = client.get_online_features(
        feature_group="user_preferences",
        entity_id=user_id
    )
    
    # Obter conteúdo relevante
    recommended_content = client.get_personalized_content(
        user_features=user_features,
        diversity_weight=0.3,
        recency_weight=0.2
    )
    
    # Registrar impressões
    client.log_content_impression(
        user_id=user_id,
        content_ids=recommended_content,
        timestamp=datetime.now()
    )
    
    return recommended_content
```

### 3. Detecção de Fraude em Tempo Real

#### Cenário
Sistema financeiro que precisa detectar transações fraudulentas em tempo real.

#### Implementação
```python
# 1. Criar feature group para detecção de fraude
fraud_group = client.create_feature_group(
    name="fraud_detection",
    description="Features para detecção de fraude",
    entity_type="transaction",
    frequency="realtime",
    online_enabled=True
)

# 2. Registrar features com janelas temporais
features = [
    {
        "name": "tx_amount_vs_avg",
        "type": "numerical",
        "transformation": """
            WITH user_avg AS (
                SELECT AVG(amount) as avg_amount
                FROM transactions
                WHERE user_id = :user_id
                AND timestamp >= NOW() - INTERVAL '30 days'
            )
            SELECT amount / user_avg.avg_amount
            FROM transactions
            CROSS JOIN user_avg
            WHERE id = :transaction_id
        """
    },
    {
        "name": "location_velocity",
        "type": "numerical",
        "transformation": """
            SELECT 
                ST_Distance(
                    current_location,
                    LAG(location) OVER (ORDER BY timestamp)
                ) / 
                EXTRACT(EPOCH FROM (
                    timestamp - LAG(timestamp) OVER (ORDER BY timestamp)
                ))
            FROM transactions
            WHERE user_id = :user_id
            ORDER BY timestamp DESC
            LIMIT 1
        """
    }
]

# 3. Uso em produção
async def check_transaction(transaction_id: str):
    # Obter features em tempo real
    features = await client.get_online_features(
        feature_group="fraud_detection",
        entity_id=transaction_id
    )
    
    # Avaliar risco
    risk_score = fraud_model.predict(features)
    
    # Atualizar feature store com resultado
    await client.log_fraud_check(
        transaction_id=transaction_id,
        risk_score=risk_score,
        timestamp=datetime.now()
    )
    
    return risk_score > FRAUD_THRESHOLD
```

### 4. Personalização de Conteúdo

#### Cenário
Plataforma de streaming que precisa personalizar conteúdo para cada usuário.

#### Implementação
```python
# 1. Criar feature groups para conteúdo e usuário
content_group = client.create_feature_group(
    name="content_features",
    description="Características do conteúdo",
    entity_type="content",
    features=[
        "genre_embedding",
        "popularity_score",
        "duration",
        "release_date"
    ]
)

user_group = client.create_feature_group(
    name="user_preferences",
    description="Preferências do usuário",
    entity_type="user",
    features=[
        "genre_preferences",
        "watch_time_distribution",
        "completion_rate"
    ]
)

# 2. Implementar lógica de personalização
def personalize_homepage(user_id: str):
    # Obter features do usuário
    user_features = client.get_online_features(
        feature_group="user_preferences",
        entity_id=user_id
    )
    
    # Obter conteúdo relevante
    recommended_content = client.get_personalized_content(
        user_features=user_features,
        diversity_weight=0.3,
        recency_weight=0.2
    )
    
    # Registrar impressões
    client.log_content_impression(
        user_id=user_id,
        content_ids=recommended_content,
        timestamp=datetime.now()
    )
    
    return recommended_content
```

### 5. Otimização de Preços

#### Cenário
Varejista que precisa otimizar preços baseado em demanda e competição.

#### Implementação
```python
# 1. Criar feature groups para precificação
pricing_group = client.create_feature_group(
    name="pricing_features",
    description="Features para otimização de preços",
    entity_type="product",
    frequency="hourly",
    features=[
        "competitor_prices",
        "stock_level",
        "demand_forecast",
        "price_elasticity"
    ]
)

# 2. Implementar lógica de precificação dinâmica
def optimize_price(product_id: str):
    # Obter features atualizadas
    features = client.get_online_features(
        feature_group="pricing_features",
        entity_id=product_id
    )
    
    # Calcular preço ótimo
    optimal_price = pricing_model.optimize(
        features=features,
        constraints={
            "min_margin": 0.1,
            "max_price_change": 0.15
        }
    )
    
    # Registrar decisão
    client.log_price_decision(
        product_id=product_id,
        price=optimal_price,
        timestamp=datetime.now()
    )
    
    return optimal_price
```

Cada caso de uso demonstra como a Feature Store pode ser utilizada para:
1. **Centralizar Features**: Manter todas as features em um lugar
2. **Garantir Consistência**: Mesmas transformações em treino e produção
3. **Monitorar Qualidade**: Acompanhar a saúde das features
4. **Otimizar Performance**: Features prontas para uso em tempo real
5. **Facilitar Colaboração**: Equipes podem compartilhar e reutilizar features

## Melhores Práticas

### 1. Nomenclatura de Features
- Use nomes descritivos: `customer_purchase_30d_avg`
- Inclua a janela temporal: `_7d_`, `_30d_`
- Indique o tipo de agregação: `_avg`, `_sum`, `_count`

### 2. Otimização de Performance
- Use índices apropriados nas tabelas fonte
- Evite joins desnecessários
- Considere materialização para features frequentemente usadas
- Use particionamento temporal quando apropriado

### 3. Documentação
- Descreva o significado da feature
- Documente pressupostos importantes
- Mantenha exemplos de valores típicos
- Liste modelos que usam a feature

### 4. Monitoramento
- Configure alertas para:
  - Latência de processamento
  - Missing values
  - Drift nos valores
  - Erros de processamento

## Troubleshooting

### Problemas Comuns e Soluções

1. **Feature não está atualizando**
   - Verifique a janela de agregação
   - Confirme se há dados novos na fonte
   - Verifique logs de processamento

2. **Valores inesperados**
   - Valide a query SQL
   - Verifique tratamento de nulls
   - Confirme timezone dos dados

3. **Performance ruim**
   - Analise o plano de execução SQL
   - Verifique índices
   - Considere materialização

4. **Erros de processamento**
   - Verifique formato dos dados
   - Confirme permissões
   - Valide conexões com fontes

## Feature Groups

### 1. Conceito
Feature Groups são conjuntos lógicos de features relacionadas. Eles ajudam a:
- Organizar features por domínio ou caso de uso
- Gerenciar permissões e acesso em grupo
- Facilitar o versionamento conjunto
- Melhorar a descoberta de features relacionadas

### 2. Criando Feature Groups

#### Via Interface Web
1. Acesse a página Feature Groups
2. Clique no botão "+"
3. Preencha os campos:
   ```
   Nome: customer_behavior
   Descrição: Features relacionadas ao comportamento do cliente
   Entity Type: customer
   Tags: behavior, customer, transactions
   Owner: time_ml
   Frequency: daily
   ```
4. Após criar o grupo, você pode:
   - Adicionar features existentes ao grupo
   - Ver estatísticas do grupo
   - Gerenciar permissões
   - Deprecar ou arquivar o grupo

#### Via Python
```python
from j_feature_store import FeatureStoreClient

client = FeatureStoreClient(FEATURE_STORE_URL)

# Criar um grupo
group = client.create_feature_group(
    name="customer_behavior",
    description="Features relacionadas ao comportamento do cliente",
    entity_type="customer",
    tags=["behavior", "customer", "transactions"],
    owner="time_ml",
    frequency="daily"
)

# Adicionar features ao grupo
client.add_features_to_group(
    group_id=group.id,
    feature_ids=[
        "customer_purchase_7d_avg",
        "customer_last_purchase_date",
        "customer_favorite_category"
    ]
)

# Obter estatísticas do grupo
stats = client.get_feature_group_statistics(group.id)
print(f"Total features: {stats['total_features']}")
print(f"Tipos de features: {stats['feature_types']}")
print(f"Score de qualidade: {stats['quality_score']}%")
```

### 3. Melhores Práticas para Feature Groups

1. **Organização Lógica**
   - Agrupe features que são frequentemente usadas juntas
   - Mantenha coerência no nível de granularidade
   - Use nomes descritivos e consistentes

2. **Documentação**
   - Descreva o propósito do grupo
   - Mantenha tags atualizadas
   - Documente dependências entre grupos

3. **Governança**
   - Atribua owners responsáveis
   - Defina frequência de atualização
   - Monitore a qualidade das features

4. **Versionamento**
   - Versione grupos de features juntos
   - Documente mudanças importantes
   - Mantenha compatibilidade backwards

### 4. Exemplos de Feature Groups

1. **Comportamento do Cliente**
   ```python
   client.create_feature_group(
       name="customer_behavior",
       description="Padrões de comportamento do cliente",
       entity_type="customer",
       features=[
           "purchase_frequency",
           "avg_basket_size",
           "preferred_payment_method"
       ]
   )
   ```

2. **Risco de Churn**
   ```python
   client.create_feature_group(
       name="churn_risk",
       description="Indicadores de risco de churn",
       entity_type="customer",
       features=[
           "days_since_last_purchase",
           "support_tickets_count",
           "payment_delays"
       ]
   )
   ```

3. **Perfil Demográfico**
   ```python
   client.create_feature_group(
       name="demographics",
       description="Características demográficas",
       entity_type="customer",
       features=[
           "age",
           "location",
           "income_bracket"
       ]
   )
   ```

## Recursos Adicionais


- [GitHub do Projeto](https://github.com/thespamer/j-feature-store)
- [Exemplos de Código](https://github.com/thespamer/j-feature-store/examples)


## Contribuindo

Encontrou um bug? Tem uma sugestão? Contribuições são bem-vindas!
- Abra uma issue no GitHub
- Envie um pull request
- Participe das discussões no Discord

---

*Este tutorial está em constante evolução. Sua contribuição é valiosa para melhorá-lo!*

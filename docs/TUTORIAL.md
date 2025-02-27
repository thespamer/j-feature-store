# Tutorial: J Feature Store para Cientistas de Dados e Analistas de ML

## Índice
1. [Introdução](#introdução)
2. [Por que usar uma Feature Store?](#por-que-usar-uma-feature-store)
3. [Conceitos Fundamentais](#conceitos-fundamentais)
4. [Primeiros Passos](#primeiros-passos)
5. [Casos de Uso Práticos](#casos-de-uso-práticos)
6. [Melhores Práticas](#melhores-práticas)
7. [Troubleshooting](#troubleshooting)

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

### 1. Features para Detecção de Fraude

```python
# Feature: número de transações por hora
client.create_feature(
    name="tx_per_hour",
    description="Número de transações por hora",
    type="numerical",
    entity_id="customer_id",
    transformation={
        "sql_query": """
            SELECT
                customer_id,
                COUNT(*) as tx_count
            FROM transactions
            WHERE 
                transaction_date >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
            GROUP BY customer_id
        """,
        "aggregation_window": "1h"
    }
)

# Feature: distância média entre transações
client.create_feature(
    name="avg_tx_distance_km",
    description="Distância média entre transações consecutivas",
    type="numerical",
    entity_id="customer_id",
    transformation={
        "sql_query": """
            WITH tx_with_lag AS (
                SELECT
                    customer_id,
                    transaction_location,
                    LAG(transaction_location) OVER (
                        PARTITION BY customer_id 
                        ORDER BY transaction_date
                    ) as prev_location
                FROM transactions
                WHERE 
                    transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
            )
            SELECT
                customer_id,
                AVG(
                    ST_Distance(
                        transaction_location,
                        prev_location
                    ) / 1000
                ) as avg_distance_km
            FROM tx_with_lag
            GROUP BY customer_id
        """,
        "aggregation_window": "1d"
    }
)
```

### 2. Features para Recomendação

```python
# Feature: categorias mais visualizadas
client.create_feature(
    name="top_viewed_categories",
    description="Top 5 categorias mais visualizadas",
    type="categorical",
    entity_id="customer_id",
    transformation={
        "sql_query": """
            WITH ranked_categories AS (
                SELECT
                    customer_id,
                    product_category,
                    COUNT(*) as view_count,
                    ROW_NUMBER() OVER (
                        PARTITION BY customer_id 
                        ORDER BY COUNT(*) DESC
                    ) as rn
                FROM product_views
                WHERE 
                    view_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
                GROUP BY 
                    customer_id,
                    product_category
            )
            SELECT
                customer_id,
                STRING_AGG(product_category, ',') as top_categories
            FROM ranked_categories
            WHERE rn <= 5
            GROUP BY customer_id
        """,
        "aggregation_window": "30d"
    }
)
```

### 3. Features para Churn Prediction

```python
# Feature: dias desde última compra
client.create_feature(
    name="days_since_last_purchase",
    description="Número de dias desde a última compra",
    type="numerical",
    entity_id="customer_id",
    transformation={
        "sql_query": """
            SELECT
                customer_id,
                DATEDIFF(
                    CURRENT_DATE(),
                    MAX(purchase_date)
                ) as days_since_purchase
            FROM purchases
            GROUP BY customer_id
        """,
        "aggregation_window": "365d"
    }
)

# Feature: tendência de gastos
client.create_feature(
    name="purchase_amount_trend",
    description="Tendência de gastos (regressão linear)",
    type="numerical",
    entity_id="customer_id",
    transformation={
        "sql_query": """
            WITH purchase_history AS (
                SELECT
                    customer_id,
                    purchase_date,
                    purchase_amount,
                    ROW_NUMBER() OVER (
                        PARTITION BY customer_id 
                        ORDER BY purchase_date
                    ) as day_number
                FROM purchases
                WHERE 
                    purchase_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
            )
            SELECT
                customer_id,
                REGR_SLOPE(purchase_amount, day_number) as amount_trend
            FROM purchase_history
            GROUP BY customer_id
        """,
        "aggregation_window": "90d"
    }
)
```

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

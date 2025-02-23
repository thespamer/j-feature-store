# Transformadores de Features

## Visão Geral

Os transformadores de features são componentes essenciais que permitem modificar, normalizar e preparar features para uso em modelos de machine learning. Nossa implementação fornece uma estrutura flexível e extensível para diferentes tipos de transformações.

## Tipos de Transformadores

### Transformador Numérico (NumericTransformer)

Responsável por transformações em features numéricas.

#### Métodos Suportados

1. **Standard Scaler**
   - Normaliza os dados para média 0 e desvio padrão 1
   - Útil quando os dados seguem uma distribuição normal
   ```python
   transformer = NumericTransformer(
       name="amount_normalizer",
       config={"method": "standard"}
   )
   ```

2. **MinMax Scaler**
   - Escala os dados para um intervalo específico (geralmente [0,1])
   - Útil quando você precisa de limites limitados
   ```python
   transformer = NumericTransformer(
       name="amount_scaler",
       config={"method": "minmax"}
   )
   ```

### Transformador Categórico (CategoricalTransformer)

Responsável por transformações em features categóricas.

#### Métodos Suportados

1. **Label Encoder**
   - Converte categorias em valores numéricos
   - Útil para variáveis categóricas ordinais
   ```python
   transformer = CategoricalTransformer(
       name="status_encoder",
       config={"method": "label"}
   )
   ```

2. **One-Hot Encoder**
   - Cria colunas binárias para cada categoria
   - Ideal para variáveis categóricas nominais
   ```python
   transformer = CategoricalTransformer(
       name="category_encoder",
       config={"method": "onehot"}
   )
   ```

## Uso com Feature Registry

Os transformadores são integrados com o Feature Registry para versionamento e rastreabilidade.

```python
# Criar e registrar uma feature com transformador
feature = Feature(
    name="transaction_amount_normalized",
    description="Valor normalizado da transação",
    type="numerical",
    entity_id="transaction"
)

# Criar e configurar transformador
transformer = NumericTransformer(
    name="amount_normalizer",
    config={"method": "standard"}
)

# Registrar feature com transformador
version = await registry.register_feature(feature, transformer)
```

## Persistência de Configurações

Os transformadores salvam automaticamente suas configurações e parâmetros aprendidos:

```python
# Configuração salva inclui:
{
    "name": "amount_normalizer",
    "type": "NumericTransformer",
    "config": {
        "method": "standard"
    },
    "fitted_params": {
        "mean": [100.5],
        "scale": [25.3]
    }
}
```

## Exemplo Completo

```python
import pandas as pd
from app.transformations import NumericTransformer
from app.services.feature_store import FeatureStore
from app.registry import FeatureRegistry

# Criar transformador
transformer = NumericTransformer(
    name="amount_normalizer",
    config={"method": "standard"}
)

# Dados de exemplo
data = pd.DataFrame({
    "amount": [100.0, 250.0, 50.0, 1000.0, 75.0]
})

# Treinar e transformar
await transformer.fit(data)
normalized = await transformer.transform(data)

# Armazenar valores transformados
for idx, value in enumerate(normalized["amount"]):
    await feature_store.store_feature_value(
        feature_id,
        {
            "entity_id": f"transaction_{idx}",
            "value": float(value)
        }
    )
```

## Extensibilidade

O sistema de transformadores é extensível. Para criar um novo transformador:

1. Herde da classe base `FeatureTransformer`
2. Implemente os métodos `transform` e `fit`
3. Defina a configuração específica do transformador

```python
class CustomTransformer(FeatureTransformer):
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        # Configuração específica aqui
    
    async def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        # Implementação da transformação
        pass
    
    async def fit(self, data: pd.DataFrame) -> None:
        # Implementação do treinamento
        pass
```

## Boas Práticas

1. **Sempre registre transformadores** junto com as features para manter rastreabilidade
2. **Armazene parâmetros de transformação** para reprodutibilidade
3. **Use transformadores assíncronos** para melhor performance
4. **Valide os dados** antes de aplicar transformações
5. **Mantenha versionamento** de features e transformadores

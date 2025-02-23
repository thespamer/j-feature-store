import asyncio
import pandas as pd
from app.transformations import NumericTransformer
from app.services.feature_store import FeatureStore
from app.registry import FeatureRegistry
from app.models.feature import Feature

async def main():
    # Criar feature store e registry
    feature_store = FeatureStore()
    registry = FeatureRegistry()
    
    # Criar uma feature de valor monetário
    feature = Feature(
        name="transaction_amount_normalized",
        description="Valor normalizado da transação",
        type="numerical",
        entity_id="transaction"
    )
    
    # Criar e registrar a feature
    feature = await feature_store.create_feature(feature)
    
    # Criar transformer com normalização
    transformer = NumericTransformer(
        name="amount_normalizer",
        config={"method": "standard"}  # Usar StandardScaler
    )
    
    # Dados de exemplo
    data = pd.DataFrame({
        "amount": [100.0, 250.0, 50.0, 1000.0, 75.0]
    })
    
    # Treinar o transformer
    await transformer.fit(data)
    
    # Transformar os dados
    normalized = await transformer.transform(data)
    
    # Registrar feature com transformer
    version = await registry.register_feature(feature, transformer)
    print(f"Feature registrada com versão {version}")
    
    # Armazenar alguns valores normalizados
    for idx, value in enumerate(normalized["amount"]):
        await feature_store.store_feature_value(
            feature.id,
            {
                "entity_id": f"transaction_{idx}",
                "value": float(value)
            }
        )
    
    # Recuperar um valor
    value = await feature_store.get_feature_value(feature.id, "transaction_0")
    print(f"Valor normalizado recuperado: {value.value}")
    
    # Buscar versão atual da feature
    feature_version = await registry.get_feature_version(feature.id)
    print(f"Configuração do transformer: {feature_version.transformer_config}")

if __name__ == "__main__":
    asyncio.run(main())

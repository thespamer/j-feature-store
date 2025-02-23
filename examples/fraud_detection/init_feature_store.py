from feature_engineering import FeatureStoreClient

def init_feature_store():
    client = FeatureStoreClient()
    
    # Grupo para transações de cartão de crédito
    client.create_feature_group(
        name="credit_card_transactions",
        description="Dados brutos de transações de cartão de crédito",
        entity_type="card",
        features=["timestamp", "amount", "merchant", "merchant_country"],
        tags=["raw", "transactions", "credit_card"],
        frequency="realtime"
    )
    
    # Grupo para features de detecção de fraude
    client.create_feature_group(
        name="fraud_detection_features",
        description="Features calculadas para detecção de fraude",
        entity_type="card",
        features=[
            "transaction_amount", "merchant_category", "merchant_country",
            "transaction_hour", "transaction_day", "is_weekend",
            "tx_count_1h", "total_amount_1h", "avg_amount_1h",
            "std_amount_1h", "unique_countries_1h", "unique_merchants_1h",
            "max_amount_1h", "min_amount_1h", "amount_velocity",
            "small_tx_ratio", "amount_ratio_to_avg", "small_amount_variations",
            "country_change_ratio"
        ],
        tags=["fraud_detection", "features", "credit_card"],
        frequency="realtime"
    )
    
    # Grupo para resultados da análise de fraude
    client.create_feature_group(
        name="fraud_analysis_results",
        description="Resultados da análise de detecção de fraude",
        entity_type="card",
        features=[
            "transaction_id", "card_id", "timestamp", "amount",
            "merchant", "merchant_country", "fraud_score",
            "risk_level", "risk_patterns"
        ],
        tags=["fraud_detection", "analysis", "credit_card"],
        frequency="realtime"
    )

if __name__ == "__main__":
    init_feature_store()
